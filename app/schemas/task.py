from datetime import date
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    """
    Task Base Pydantic Schema
    """

    date: date
    title: Optional[str] = ""
    note: Optional[str] = ""
    is_completed: bool = False
    order: int
    repeatable_id: Optional[str] = None
    repeatable_days: Optional[int] = None


class TaskCreate(BaseModel):
    """
    Task Create Pydantic Schema
    """

    date: date
    title: Optional[str] = ""
    note: Optional[str] = ""
    is_completed: bool = False
    order: int
    repeatable_id: Optional[str] = None
    repeatable_days: Optional[int] = None


class TaskUpdate(BaseModel):
    """
    Task Update Pydantic Schema
    """

    date: Optional[date] = None
    title: Optional[str] = None
    note: Optional[str] = None
    is_completed: Optional[bool] = None
    order: Optional[int] = None


class TaskOut(TaskCreate):
    """
    Task Out Pydantic Schema
    """

    id: int

    class Config:
        from_attributes = True
