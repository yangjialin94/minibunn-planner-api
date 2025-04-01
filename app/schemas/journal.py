from datetime import date
from typing import Optional

from pydantic import BaseModel


class JournalBase(BaseModel):
    """
    Journal Base Pydantic Schema
    """

    date: date
    subject: Optional[str] = ""
    entry: Optional[str] = ""


class JournalCreate(BaseModel):
    """
    Journal Create Pydantic Schema
    """

    date: date
    subject: Optional[str] = ""
    entry: Optional[str] = ""


class JournalUpdate(BaseModel):
    """
    Journal Update Pydantic Schema
    """

    date: Optional[date] = None
    subject: Optional[str] = None
    entry: Optional[str] = None


class JournalOut(JournalCreate):
    """
    Journal Out Pydantic Schema
    """

    id: int

    class Config:
        from_attributes = True
