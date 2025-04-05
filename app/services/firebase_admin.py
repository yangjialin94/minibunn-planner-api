import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

# Check if Firebase Admin has already been initialized to prevent reinitialization errors.
if not firebase_admin._apps:
    cred = credentials.Certificate("app/services/firebase_service_account.json")
    firebase_admin.initialize_app(cred)


# Re-export firebase_auth for convenience in other modules.
__all__ = ["firebase_auth"]
