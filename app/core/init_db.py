from datetime import date

from sqlalchemy.orm import Session

from app.core.test_data import test_journals, test_tasks
from app.models.journal import Journal
from app.models.task import Task
from app.models.user import User


def init_test_data(db: Session):
    existing = db.query(User).filter(User.id == 1).first()
    if not existing:
        user = User(
            id=1,
            firebase_uid="test_uid",
            name="Test User",
            email="test@example.com",
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
