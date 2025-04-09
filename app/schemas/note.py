from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    """
    Note Create Pydantic Schema (for POST requests)
    """

    detail: Optional[str] = ""


class NoteUpdate(BaseModel):
    """
    Note Update Pydantic Schema (for PUT requests)
    """

    detail: Optional[str] = None
    order: Optional[int] = None


class NoteOut(BaseModel):
    """
    Note Out Pydantic Schema (response to client)
    """

    id: int
    date: date
    detail: Optional[str]
    order: int

    model_config = ConfigDict(from_attributes=True)
