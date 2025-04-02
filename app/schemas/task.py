from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    """
    Task Create Pydantic Schema (for POST requests)
    """

    date: date
    title: Optional[str] = ""
    note: Optional[str] = ""
    is_completed: bool = False
    repeatable_id: Optional[str] = None
    repeatable_days: Optional[int] = None


class TaskUpdate(BaseModel):
    """
    Task Update Pydantic Schema (for PUT requests)
    """

    date: Optional[date] = None
    title: Optional[str] = None
    note: Optional[str] = None
    is_completed: Optional[bool] = None
    order: Optional[int] = None


class TaskOut(BaseModel):
    """
    Task Out Pydantic Schema (response to client)
    """

    id: int
    date: date
    title: Optional[str]
    note: Optional[str]
    is_completed: bool
    order: int
    repeatable_id: Optional[str]
    repeatable_days: Optional[int]

    model_config = ConfigDict(from_attributes=True)
