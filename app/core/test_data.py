# test_data.py
from datetime import date, timedelta
from uuid import uuid4

today = date.today()

test_tasks = [
    # Single tasks
    {
        "user_id": 1,
        "date": today,
        "title": "Buy groceries",
        "note": "Milk, eggs, bread",
        "is_completed": False,
        "order": 1,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=1),
        "title": "Workout",
        "note": "Leg day at the gym",
        "is_completed": False,
        "order": 1,
    },
    # Repeated task (3-day journal)
    {
        "user_id": 1,
        "date": today,
        "title": "Write journal",
        "note": "Reflect on the day",
        "is_completed": False,
        "order": 2,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=1),
        "title": "Write journal",
        "note": "Reflect on the day",
        "is_completed": False,
        "order": 2,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=2),
        "title": "Write journal",
        "note": "Reflect on the day",
        "is_completed": False,
        "order": 1,
    },
    # Repeated task (2-day task)
    {
        "user_id": 1,
        "date": today,
        "title": "Study React",
        "note": "Go through useEffect deep dive",
        "is_completed": False,
        "order": 3,
    },
    {
        "user_id": 1,
        "date": today + timedelta(days=1),
        "title": "Study React",
        "note": "Go through useEffect deep dive",
        "is_completed": False,
        "order": 3,
    },
]

test_journals = [
    {
        "user_id": 1,
        "date": today - timedelta(days=3),
        "subject": "Good Old Days",
        "entry": (
            "Super happy to meet with old friends we used to hang out with all the time back in Chicago!\n"
            "Need to do this more often!"
        ),
    },
    {
        "user_id": 1,
        "date": today - timedelta(days=2),
        "subject": "Reflection on Goals",
        "entry": (
            "Spent some time revisiting my goals for the year.\n"
            "I'm a bit behind on fitness, but ahead on learning."
        ),
    },
    {
        "user_id": 1,
        "date": today - timedelta(days=1),
        "subject": "Solo Adventure",
        "entry": (
            "Tried hiking alone for the first time. Peaceful but also spooky near the end.\n"
            "Not sure I'd do it again without a buddy."
        ),
    },
    {
        "user_id": 1,
        "date": today,
        "subject": "Tech Dive",
        "entry": (
            "Finally understood how useEffect cleanup works in React.\n"
            "Also cleaned up my GitHub profile a bit."
        ),
    },
]
