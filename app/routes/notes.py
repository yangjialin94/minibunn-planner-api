from datetime import date, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps.auth import get_user_id
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate

# Create a router
router = APIRouter()


@router.get("/", response_model=List[NoteOut])
def get_notes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Get notes for the current user.
    """
    query = db.query(Note).filter(Note.user_id == user_id)
    return query.order_by(Note.order).all()


@router.post("/", response_model=NoteOut)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Create a new note for the current user.
    """
    # Add default detail if not provided
    if not note.detail:
        note.detail = "New note"

    # Create the note
    max_order = (
        db.query(func.coalesce(func.max(Note.order), 0))
        .filter(Note.user_id == user_id)
        .scalar()
    )
    new_note = Note(
        user_id=user_id,
        date=date.today(),
        detail=note.detail,
        order=max_order + 1,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.patch("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: int,
    updates: NoteUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Update a note for the current user.
    """
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = updates.model_dump(exclude_unset=True)

    # Enforce only one type of update at a time
    update_fields = set(update_data.keys())
    groups = {
        "order": {"order"},
        "detail": {"detail"},
    }

    matched_groups = [group for group, keys in groups.items() if update_fields & keys]
    if len(matched_groups) > 1:
        raise HTTPException(
            status_code=400,
            detail="Only one type of update is allowed per request (order or detail).",
        )

    # Handle order update
    if "order" in update_fields:
        new_order = update_data.get("order")
        if new_order < 1:
            raise HTTPException(status_code=400, detail="Order must be 1 or greater")

        other_notes = (
            db.query(Note)
            .filter(Note.user_id == user_id, Note.id != note_id)
            .order_by(Note.order)
            .all()
        )

        # Ensure the new order is within the valid range
        max_order = len(other_notes) + 1
        if new_order > max_order:
            new_order = max_order

        for t in other_notes:
            # Shift notes down
            if note.order < new_order:
                if note.order < t.order <= new_order:
                    t.order -= 1
            # Shift notes up
            else:
                if new_order <= t.order < note.order:
                    t.order += 1

        note.order = new_order

    # Handle detail and date update
    elif {"detail"} & update_fields:
        note.detail = update_data.get("detail")
        note.date = date.today()

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    """
    Delete a note for the current user.
    """
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note_order = note.order

    db.delete(note)
    db.commit()

    # Reorder the remaining notes
    remaining_notes = (
        db.query(Note)
        .filter(Note.user_id == user_id, Note.order > note_order)
        .order_by(Note.order)
        .all()
    )

    for t in remaining_notes:
        t.order -= 1

    db.commit()
    return {"message": "Note deleted and remaining reordered"}
