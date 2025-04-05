"""
These routes are only for testing purposes.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserOut

# Create a router
router = APIRouter()


@router.get("/", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
):
    """
    Get all users along with their tasks and journals.
    """
    users = (
        db.query(User)
        .options(joinedload(User.tasks), joinedload(User.journals))
        .order_by(User.id)
        .all()
    )
    return users


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by user id along with their tasks and journals.
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
