from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User Database Schema / SQLAlchemy ORM Model
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    journals = relationship(
        "Journal", back_populates="user", cascade="all, delete-orphan"
    )
