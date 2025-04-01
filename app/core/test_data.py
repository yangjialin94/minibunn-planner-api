# test_data.py
from datetime import date

test_tasks = [
    # 📅 2025-03-23
    {
        "user_id": 1,
        "title": "Family Breakfast",
        "note": "Enjoy breakfast with family.",
        "date": date(2025, 3, 23),
        "is_completed": False,
        "order": 1,
    },
    # 📅 2025-03-24
    {
        "user_id": 1,
        "title": "Office Meeting",
        "note": "Weekly planning meeting.",
        "date": date(2025, 3, 24),
        "is_completed": False,
        "order": 1,
    },
    # 📅 2025-03-25
    {
        "user_id": 1,
        "title": "Client Call",
        "note": "Discuss project details.",
        "date": date(2025, 3, 25),
        "is_completed": False,
        "order": 1,
    },
    # 📅 2025-03-26
    {
        "user_id": 1,
        "title": "Code Review",
        "note": "Review the latest commits.",
        "date": date(2025, 3, 26),
        "is_completed": True,
        "order": 1,
    },
    # 📅 2025-03-27
    {
        "user_id": 1,
        "title": "Team Sync",
        "note": "Quick sync-up with the team.",
        "date": date(2025, 3, 27),
        "is_completed": False,
        "order": 1,
    },
    # 📅 2025-03-28
    {
        "user_id": 1,
        "title": "Morning Exercise",
        "note": "Jog for 30 minutes.",
        "date": date(2025, 3, 28),
        "is_completed": True,
        "order": 1,
    },
    {
        "user_id": 1,
        "title": "Buy Groceries",
        "note": "Remember to pick up milk, eggs, and bread.",
        "date": date(2025, 3, 28),
        "is_completed": False,
        "order": 2,
    },
    {
        "user_id": 1,
        "title": "Team Meeting",
        "note": "Discuss project updates with the team.",
        "date": date(2025, 3, 28),
        "is_completed": False,
        "order": 3,
    },
    # 📅 2025-03-29
    {
        "user_id": 1,
        "title": "Evening Walk",
        "note": "Relax with an evening walk after dinner.",
        "date": date(2025, 3, 29),
        "is_completed": False,
        "order": 1,
    },
    # 📅 2025-03-30
    {
        "user_id": 1,
        "title": "Dinner with Hanwen",
        "note": "Find a hotpot place.",
        "date": date(2025, 3, 30),
        "is_completed": False,
        "order": 1,
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
