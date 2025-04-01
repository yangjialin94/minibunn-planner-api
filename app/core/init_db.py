# core/init_db.py
from datetime import date

from core.test_data import test_journals, test_tasks
from models.journal import Journal
from models.task import Task
from models.user import User
from sqlalchemy.orm import Session


def init_test_data(db: Session):
    existing = db.query(User).filter(User.id == 1).first()
    if not existing:
        user = User(
            id=1,
            firebase_auth_token="test_uid",
            name="Test User",
            email="test@example.com",
            created_date=date.today(),
            subscription_status="free",
            last_paid_date=None,
        )
        db.add(user)
        db.commit()

    for task_data in test_tasks:
        task = Task(**task_data)
        db.merge(task)  # merge allows updating or inserting by primary key
    for journal_data in test_journals:
        journal = Journal(**journal_data)
        db.merge(journal)

    db.commit()
