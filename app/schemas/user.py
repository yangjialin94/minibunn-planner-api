from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.journal import JournalOut
from app.schemas.note import NoteOut
from app.schemas.task import TaskOut


class UserOut(BaseModel):
    """
    User Out Pydantic Schema (response to client)
    """

    id: int
    firebase_uid: str
    name: Optional[str]
    email: str

    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    subscription_status: Optional[str]
    is_subscribed: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class UserOutFull(BaseModel):
    """
    User Out Pydantic Schema (response to client)
    """

    id: int
    firebase_uid: str
    name: Optional[str]
    email: str

    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    subscription_status: Optional[str]
    is_subscribed: Optional[bool] = False

    tasks: List[TaskOut] = []
    notes: List[NoteOut] = []
    journals: List[JournalOut] = []

    model_config = ConfigDict(from_attributes=True)
