# Run

```bash
source .venv/bin/activate
univorn app.main:app --reload
```

## Environment File

```txt
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
WEB_URL=http://localhost:3000
ENV=dev
```

# Test

- Reload initial data:

    ```bash
    python3 -m app.scripts.init_test_data
    ```

- Run unit tests:

    ```bash
    pytest -v
    ```

# Standard DB Migration

1. Modify your SQLAlchemy models (`app/models/xxx`).
2. Autogenerate a migration file

    ```bash
    alembic revision --autogenerate -m "Put comment here"
    ```

3. Apply the migration

    ```bash
    alembic upgrade head
    ```

# More Alembic scripts

- View DB Status:

    ```bash
    alembic current
    ```

- See migration history:

    ```bash
    alembic history
    ```

- Downgrade if needed:

    ```bash
    alembic downgrade -1  # go back one migration
    ```

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
