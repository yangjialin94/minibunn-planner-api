# test_data.py
from datetime import date, timedelta
from uuid import uuid4

today = date.today()
repeatable_id_1 = str(uuid4())
repeatable_id_2 = str(uuid4())

test_tasks = [
    # Single tasks
    {
        "user_id": 1,
        "date": today,
        "title": "Buy groceries",
        "note": "Milk, eggs, bread",
        "is_completed": False,
        "order": 1,
        "repeatable_id": None,
        "repeatable_days": None,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=1),
        "title": "Workout",
        "note": "Leg day at the gym",
        "is_completed": False,
        "order": 1,
        "repeatable_id": None,
        "repeatable_days": None,
    },
    # Repeated task (3-day journal)
    {
        "user_id": 1,
        "date": today,
        "title": "Write journal",
        "note": "Reflect on the day",
        "is_completed": False,
        "order": 2,
        "repeatable_id": repeatable_id_1,
        "repeatable_days": 3,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=1),
        "title": "Write journal",
        "note": "Reflect on the day",
        "is_completed": False,
        "order": 2,
        "repeatable_id": repeatable_id_1,
        "repeatable_days": 3,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=2),
        "title": "Write journal",
        "note": "Reflect on the day",
        "is_completed": False,
        "order": 1,
        "repeatable_id": repeatable_id_1,
        "repeatable_days": 3,
    },
    # Repeated task (2-day task)
    {
        "user_id": 1,
        "date": today,
        "title": "Study React",
        "note": "Go through useEffect deep dive",
        "is_completed": False,
        "order": 3,
        "repeatable_id": repeatable_id_2,
        "repeatable_days": 2,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=1),
        "title": "Study React",
        "note": "Go through useEffect deep dive",
        "is_completed": False,
        "order": 3,
        "repeatable_id": repeatable_id_2,
        "repeatable_days": 2,
    },
]

test_journals = [
    {
        "user_id": 1,
        "date": date(2025, 3, 29),
        "subject": "Good Old Days",
        "entry": (
            "Super happy to met with old friends we used to hangout with all the time back in Chicago!\n"
            "Need to do this more often!"
        ),
    }
]
