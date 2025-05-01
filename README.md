# Documentation

## Local Run

```bash
source .venv/bin/activate
univorn app.main:app --reload
```

```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

## Environment Variables

```txt
ENV=dev

DATABASE_URL=postgresql://user:password@localhost:5432/MinimalPlanner
WEB_URL=http://localhost:3000

STRIPE_SECRET_KEY=sk_test_
STRIPE_WEBHOOK_SECRET=whsec_

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

## Release

1. Create an annotated tag

   ```bash
   git tag -a v1.0.0 -m "comment"
   git push origin v1.0.0
   ```

2. Draft a GitHub Release on that tag
   - Go to Releases → Draft a new release
   - Select your new tag
   - Fill in a “What’s changed” summary or changelog items
   - Publish
