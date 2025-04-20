# Documentation

## Run

```bash
source .venv/bin/activate
univorn app.main:app --reload
```

## Environment Variables

```txt
ENV=dev

DATABASE_URL=postgresql://user:password@localhost:5432/MinimalPlanner
WEB_URL=http://localhost:3000

STRIPE_SECRET_KEY=sk_test_51RECIKRSBgEYMFnWnnje2seL2FbIvmbW2nanuTT5tGvLZkQQRLJaL8s9WrJAvF8rQ5y7xWH8JXI2Jp5CBbIuQQSd00y7oQq8Fb
STRIPE_WEBHOOK_SECRET=whsec_128ff2317901455dad859951c50fe03034e8fc08c7f8b81368e4bd185de7fba0

TRIAL_DAYS=1
```

## Test

- Reload initial data:

    ```bash
    python3 -m app.scripts.init_test_data
    ```

- Run unit tests:

    ```bash
    pytest -v
    ```

- Test Stripe webhooks:

    ```bash
    stripe listen --forward-to localhost:8000/api/stripe/webhook
    ```

## Standard DB Migration

1. Modify your SQLAlchemy models (`app/models/xxx`).
2. Autogenerate a migration file

    ```bash
    alembic revision --autogenerate -m "Put comment here"
    ```

3. Apply the migration

    ```bash
    alembic upgrade head
    ```

## More Alembic scripts

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

## File Structure

```text
app/
├── api/
│   ├── deps/                   # Shared dependencies (e.g., get_user)
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
