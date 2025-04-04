from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_user_id
from app.models.journal import Journal
from app.schemas.journal import JournalOut, JournalUpdate

# Create a router
router = APIRouter()


@router.get("/", response_model=JournalOut)
def get_or_create_journal(
    date: date,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Get the journal for the given date.
    If it doesn't exist, create a new one and return it.
    """
    # Get the journal for the specified date
    journal = (
        db.query(Journal)
        .filter(Journal.user_id == user_id, Journal.date == date)
        .first()
    )
    if journal:
        return journal

    # Create a new journal if it doesn't exist
    new_journal = Journal(date=date, user_id=user_id, subject="", entry="")
    db.add(new_journal)
    db.commit()
    db.refresh(new_journal)
    return new_journal


# @router.post("/", response_model=JournalOut)
# def create_journal(
#     journal: JournalCreate,
#     db: Session = Depends(get_db),
#     user_id: int = Depends(get_user_id),
# ):
#     """
#     Create a new journal for the current user.
#     """
#     # Check if journal already exists for this date
#     existing = (
#         db.query(Journal)
#         .filter(Journal.user_id == user_id, Journal.date == journal.date)
#         .first()
#     )
#     if existing:
#         raise HTTPException(
#             status_code=400, detail="Journal already exists for this date"
#         )

#     # Create the journal
#     db_journal = Journal(**journal.model_dump(), user_id=user_id)
#     db.add(db_journal)
#     db.commit()
#     db.refresh(db_journal)
#     return db_journal


@router.patch("/{journal_id}", response_model=JournalOut)
def update_journal(
    journal_id: int,
    updates: JournalUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Update a journal for the current user.
    """
    # Check if journal exists
    journal = (
        db.query(Journal)
        .filter(Journal.id == journal_id, Journal.user_id == user_id)
        .first()
    )
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    # Update the journal
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(journal, key, value)

    db.commit()
    db.refresh(journal)
    return journal
