# File Structure

```
app/
├── api/
│   ├── deps/                   # Shared dependencies (e.g., get_user_id)
│   │   └── auth.py
│   ├── routes/                 # Route definitions
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── journals.py
│   └── main.py                 # App entry point
├── core/                       # Core config, settings, startup logic
│   ├── config.py
│   ├── database.py
│   └── init_db.py              # Optional DB seeding/init
├── models/                     # SQLAlchemy models
│   ├── __init__.py
│   └── user.py
│   └── task.py
│   └── journal.py
├── schemas/                    # Pydantic schemas
│   ├── __init__.py
│   └── task.py
│   └── journal.py
│   └── user.py
├── services/                   # Business logic, sync jobs, complex ops
│   └── task_service.py
│   └── journal_service.py
├── utils/                      # Helper modules (e.g., date, ordering)
│   └── ordering.py
│   └── firebase.py
├── tests/                      # Pytest unit & integration tests
│   ├── test_tasks.py
│   └── test_journals.py
└── __init__.py
```
