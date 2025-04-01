from core.database import Base
from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    """
    User Database Schema / SQLAlchemy ORM Model
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_auth_token = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_date = Column(Date)
    subscription_status = Column(String)
    last_paid_date = Column(Date)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    journals = relationship(
        "Journal", back_populates="user", cascade="all, delete-orphan"
    )
