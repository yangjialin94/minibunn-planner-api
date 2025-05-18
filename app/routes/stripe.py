import logging
import os
from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from firebase_admin import auth
from sqlalchemy.orm import Session

from app.core.config import TRIAL_DAYS
from app.core.database import get_db
from app.deps.auth import get_subscribed_user, get_user
from app.models.user import User
from app.schemas.stripe import CheckoutSessionCreate, StripeCheckout, SubscriptionStatus

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/subscription-status", response_model=SubscriptionStatus)
def get_subscription_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    """
    Get the current subscription status for the user.
    """
    if not user.stripe_subscription_id:
        if user.subscription_status == "lifetime":
            return {
                "is_subscribed": True,
                "status": "lifetime",
                "period_end_date": None,
                "cancel_at_period_end": None,
                "plan_name": "Lifetime Access",
                "price_amount": 29.99,
                "price_currency": "USD",
            }
        return JSONResponse(
            {
                "is_subscribed": False,
                "status": "none",
                "period_end_date": None,
                "cancel_at_period_end": None,
                "plan_name": None,
                "price_amount": None,
                "price_currency": None,
            }
        )

    try:
        # Retrieve the subscription from Stripe
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id, expand=["items.data.price.product"]
        )

        # Parse the subscription details
        item = subscription["items"]["data"][0]
        period_end_timestamp = item.get("current_period_end") or subscription.get(
            "trial_end"
        )
        period_end_date = (
            datetime.fromtimestamp(period_end_timestamp).strftime("%b %d, %Y")
            if period_end_timestamp
            else None
        )
        price = item["price"]
        product = price["product"]

        # Return the subscription status
        return {
            "is_subscribed": subscription["status"] == "active",
            "status": subscription["status"],
            "period_end_date": period_end_date,
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            "plan_name": product["name"],
            "price_amount": round(price["unit_amount"] / 100, 2),
            "price_currency": price["currency"].upper(),
        }

    except stripe.error.StripeError as e:
        logger.exception(
            "Stripe error while creating checkout session | "
            "type=%s code=%s param=%s message=%s",
            e.error.type,
            e.error.code,
            e.error.param,
            e.error.message,
        )
        raise HTTPException(
            status_code=502,
            detail=e.error.message or "Stripe error",
        )


@router.post("/create-checkout-session", response_model=StripeCheckout)
async def create_checkout_session(
    checkout_session: CheckoutSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    """
    Create a Stripe Checkout session for a user.
    """
    # Get the user's Firebase UID and email
    firebase_uid = user.firebase_uid
    email = user.email

    # Create a Stripe customer if the user doesn't have one
    try:
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=email)

            # Update the user with the Stripe customer ID
            user.stripe_customer_id = customer.id
            db.commit()
    except stripe.error.StripeError as e:
        logger.exception(
            "Stripe error while creating checkout session | "
            "type=%s code=%s param=%s message=%s",
            e.error.type,
            e.error.code,
            e.error.param,
            e.error.message,
        )
        raise HTTPException(
            status_code=502,
            detail=e.error.message or "Stripe error",
        )

    # Check for any past or active subscriptions
    try:
        subscriptions = stripe.Subscription.list(
            customer=user.stripe_customer_id,
            status="all",
            limit=1,
        )
        has_previous_subscription = len(subscriptions.data) > 0
    except stripe.error.StripeError as e:
        logger.exception(
            "Stripe error while creating checkout session | "
            "type=%s code=%s param=%s message=%s",
            e.error.type,
            e.error.code,
            e.error.param,
            e.error.message,
        )
        raise HTTPException(
            status_code=502,
            detail=e.error.message or "Stripe error",
        )

    # Create a Stripe Checkout session
    try:
        subscription_data = (
            {
                "trial_period_days": TRIAL_DAYS,
                "trial_settings": {
                    "end_behavior": {
                        "missing_payment_method": "cancel",
                    }
                },
            }
            if not has_previous_subscription and checkout_session.mode == "subscription"
            else {}
        )

        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            mode=checkout_session.mode,
            line_items=[{"price": checkout_session.price_id, "quantity": 1}],
            **(
                {"subscription_data": subscription_data}
                if checkout_session.mode == "subscription"
                else {}
            ),
            success_url=checkout_session.success_url,
            cancel_url=checkout_session.cancel_url,
        )

        # Return the session URL
        return {"url": session.url}
    except stripe.error.StripeError as e:
        logger.exception(
            "Stripe error while creating checkout session | "
            "type=%s code=%s param=%s message=%s",
            e.error.type,
            e.error.code,
            e.error.param,
            e.error.message,
        )
        raise HTTPException(
            status_code=502,
            detail=e.error.message or "Stripe error",
        )


@router.post("/cancel-subscription")
def cancel_subscription(
    db: Session = Depends(get_db),
    user: User = Depends(get_subscribed_user),
):
    """
    Cancel the user's active Stripe subscription.
    """
    if not user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription to cancel.")

    try:
        # Cancel at period end (or use cancel_now=True to cancel immediately)
        stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True,
        )

        # Update local status immediately (optional: delay until webhook arrives)
        user.subscription_status = "canceled"
        db.commit()

        return {
            "message": "Subscription will be canceled at the end of the current billing period."
        }

    except stripe.error.StripeError as e:
        logger.exception(
            "Stripe error while creating checkout session | "
            "type=%s code=%s param=%s message=%s",
            e.error.type,
            e.error.code,
            e.error.param,
            e.error.message,
        )
        raise HTTPException(
            status_code=502,
            detail=e.error.message or "Stripe error",
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe post-checkout events.
    """
    # Verify the Stripe webhook signature
    payload = (await request.body()).decode("utf-8")
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    print("STRIPE_PAYLOAD:", payload)
    print("STRIPE_SIG_HEADER:", sig_header)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        raise HTTPException(400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Stripe signature verification failed:", e)
        raise HTTPException(400, detail="Invalid signature")

    # Get the event type and data object
    event_type = event["type"]
    data_object = event["data"]["object"]
    customer_id = data_object.get("customer")

    if event_type == "checkout.session.completed":
        subscription_id = data_object.get("subscription")
        mode = data_object.get("mode")  # "subscription" or "payment"
        user = db.query(User).filter_by(stripe_customer_id=customer_id).first()

        if user:
            user.is_subscribed = True

            if subscription_id and mode == "subscription":
                # Update the user's subscription status
                if (
                    user.stripe_subscription_id
                    and user.stripe_subscription_id != subscription_id
                ):
                    # Cancel old subscription if it exists
                    try:
                        stripe.Subscription.delete(user.stripe_subscription_id)
                    except stripe.error.StripeError as e:
                        logger.warning("Failed to cancel old subscription: %s", e)

                user.stripe_subscription_id = subscription_id
                user.subscription_status = "active"
            elif mode == "payment":
                user.subscription_status = "lifetime"
                user.plan_name = "Lifetime Access"

                # Cancel old subscription if it exists
                if user.stripe_subscription_id:
                    try:
                        stripe.Subscription.delete(user.stripe_subscription_id)
                    except stripe.error.StripeError as e:
                        logger.warning("Failed to cancel old subscription: %s", e)

                    user.stripe_subscription_id = None

            db.commit()

    elif event_type == "invoice.paid":
        # Payment succeeded for an invoice (e.g. recurring payments)
        user = db.query(User).filter_by(stripe_customer_id=customer_id).first()

        if user:
            user.is_subscribed = True
            user.subscription_status = "active"
            db.commit()

    elif event_type == "customer.subscription.updated":
        # Update subscription details when Stripe updates them
        subscription_id = data_object.get("id")
        status = data_object.get(
            "status"
        )  # can be active, trialing, past_due, canceled, etc.
        user = db.query(User).filter_by(stripe_customer_id=customer_id).first()

        if user:
            user.stripe_subscription_id = subscription_id
            user.subscription_status = status
            user.is_subscribed = status in ("active", "trialing")
            db.commit()

    elif event_type == "customer.subscription.deleted":
        # A subscription was canceled or deleted.
        subscription_id = data_object.get("id")
        customer_id = data_object.get("customer")
        user = db.query(User).filter_by(stripe_customer_id=customer_id).first()

        # Check if the user has a subscription linked to the customer ID
        if user and user.stripe_subscription_id == subscription_id:
            if data_object.get("cancel_at_period_end"):
                user.subscription_status = "canceled"
            else:
                user.subscription_status = "deleted"
                user.is_subscribed = False
                user.stripe_subscription_id = None

            db.commit()

            db.commit()

    elif event_type == "invoice.payment_failed":
        # Payment failed; mark subscription as inactive.
        customer_id = data_object.get("customer")
        user = db.query(User).filter_by(stripe_customer_id=customer_id).first()

        if user:
            user.is_subscribed = False
            user.subscription_status = "past_due"
            db.commit()

    else:
        logger.warning(
            f"Customer ID {customer_id or '[unknown]'} not linked to any user."
        )

    return {"received": True}
