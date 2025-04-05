import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.firebase_admin import firebase_auth

# Use HTTPBearer to extract the token from the Authorization header.
security = HTTPBearer()


def get_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Verify the token using Firebase Admin SDK
    token = credentials.credentials

    try:
        decoded_token = firebase_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    firebase_uid = decoded_token.get("uid")
    name = decoded_token.get("name")
    email = decoded_token.get("email")

    print(f"firebase_uid: {firebase_uid}")
    print(f"name: {name}")
    print(f"email: {email}")

    # Check if the user exists in the database
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()

    if user:
        return user.id
    else:
        # If the user does not exist, create a new user
        new_user = User(
            firebase_uid=firebase_uid,
            name=name,
            email=decoded_token.get("email"),
        )
        db.add(new_user)
        db.commit()

        print(f"New user created: {new_user}")

        db.refresh(new_user)
        return new_user.id
