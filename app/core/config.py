import os

import stripe
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file into environment

# Set up Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Load environment variables
ENV = os.getenv("ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "")
WEB_URL = os.getenv("WEB_URL", "*")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
TRIAL_DAYS = os.getenv("TRIAL_DAYS", 7)

# Set up CORS origins based on environment
if ENV == "dev":
    ALLOW_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    ALLOW_ORIGINS = [WEB_URL]
