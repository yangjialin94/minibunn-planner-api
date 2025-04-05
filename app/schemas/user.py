from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.journal import JournalOut
from app.schemas.task import TaskOut


class UserOut(BaseModel):
    """
    User Out Pydantic Schema (response to client)
    """

    id: int
    firebase_uid: str
    name: Optional[str]
    email: str
    tasks: List[TaskOut] = []
    journals: List[JournalOut] = []

    model_config = ConfigDict(from_attributes=True)
