"""
These routes are only for testing purposes.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.deps.auth import get_token
from app.models.user import User
from app.schemas.user import UserOut, UserOutFull

# Create a router
router = APIRouter()


@router.get("/all", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
):
    """
    Get all users along with their tasks and journals.
    This is for testing purposes only.
    """
    users = (
        db.query(User)
        .options(joinedload(User.tasks), joinedload(User.journals))
        .order_by(User.id)
        .all()
    )
    return users


@router.get("/by_id{user_id}", response_model=UserOutFull)
def get_user_with_data(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by user id along with their tasks and journals.
    This is for testing purposes only.
    """
    user = (
        db.query(User)
        .options(joinedload(User.tasks), joinedload(User.journals))
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/get_current", response_model=UserOut)
def get_current_user(
    db: Session = Depends(get_db),
    decoded_token: dict = Depends(get_token),
) -> User:
    """
    Get the current user.
    Create a new user if it does not exist.
    """
    # Get the user information from the decoded token
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    name = decoded_token.get("name")

    # Check if the user exists by Firebase UID
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user:
        return user

    # If the user does not exist, create a new user
    new_user = User(
        firebase_uid=firebase_uid,
        name=name,
        email=email,
        is_subscribed=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"New user created: {new_user}")
    return new_user
