# app/scheduler.py

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.journal import Journal


def delete_empty_journals():
    """
    Deletes all journal entries that are empty (i.e., have no subject or entry).
    """
    db = SessionLocal()

    try:
        empty_journals = (
            db.query(Journal).filter(Journal.subject == "", Journal.entry == "").all()
        )
        for journal in empty_journals:
            db.delete(journal)
        db.commit()
        print(f"{datetime.now()}: Deleted {len(empty_journals)} empty journals.")
    except Exception as e:
        db.rollback()
        print(f"Error deleting empty journals: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Initializes the APScheduler and schedules the delete_empty_journals job
    to run every day at midnight.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_empty_journals, "cron", hour=0, minute=0)
    scheduler.start()
