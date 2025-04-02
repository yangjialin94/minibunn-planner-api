from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Journal(Base):
    """
    Journal Database Schema / SQLAlchemy ORM Model
    """

    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    subject = Column(String)
    entry = Column(String)

    user = relationship("User", back_populates="journals")
