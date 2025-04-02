from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_user_id
from app.models.journal import Journal
from app.schemas.journal import JournalCreate, JournalOut

# Create a router
router = APIRouter()


@router.get("/", response_model=List[JournalOut])
def get_journals(
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Get journals for the current user between the start and end dates.
    """
    query = db.query(Journal).filter(Journal.user_id == user_id)
    if start and end:
        query = query.filter(Journal.date.between(start, end))
    return query.all()


@router.post("/", response_model=JournalOut)
def create_journal(
    journal: JournalCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Create a new journal for the current user.
    """
    db_journal = Journal(**journal.dict(), user_id=user_id)
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal
