from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class JournalCreate(BaseModel):
    """
    Journal Create Pydantic Schema (for POST requests)
    """

    date: date
    subject: Optional[str] = ""
    entry: Optional[str] = ""


class JournalUpdate(BaseModel):
    """
    Journal Update Pydantic Schema (for PUT requests)
    """

    date: Optional[date] = None
    subject: Optional[str] = None
    entry: Optional[str] = None


class JournalOut(BaseModel):
    """
    Journal Out Pydantic Schema (response to client)
    """

    id: int
    date: date
    subject: Optional[str] = ""
    entry: Optional[str] = ""

    model_config = ConfigDict(from_attributes=True)
