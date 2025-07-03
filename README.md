# Minibunn Planner (API)

Minibunn Planner API is the backend service for the Minibunn Planner application. It provides server-side logic, database management, and APIs for tasks, notes, journals, calendars, and user management. This repository is public to allow anyone interested to review the codebase and understand the project's structure and implementation. It is not intended for forks or external contributions.

## Features

- **Task Management**: APIs for creating, updating, and managing tasks.
- **Notes**: APIs for creating and organizing notes.
- **Journals**: APIs for maintaining daily journals.
- **Calendar**: APIs for managing events by date.
- **User Management**: APIs for managing user accounts, subscriptions, and authentication.

## Tech Stack

Minibunn Planner API is built using the following technologies:

- **Language**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Authentication**: Firebase Authentication
- **Payment Integration**: Stripe
- **Task Scheduling**: APScheduler
- **Environment Management**: Python-dotenv
- **Database Migrations**: Alembic
- **Testing**: Pytest
- **Hosting**: Render
- **Syntax Checking**: Black

## Project Structure

The project is organized as follows:

```plaintext
app/
  core/               # Core configurations and utilities
  deps/               # Dependency injection modules
  models/             # SQLAlchemy ORM models
  routes/             # API route handlers
  schemas/            # Pydantic schemas for request/response validation
  services/           # Business logic and integrations (e.g., Firebase, Stripe)
  tests/              # Unit and integration tests
migrations/           # Database migration scripts
```

## Environment Variables

The following environment variables are required:

```txt
# General
ENV=dev
DATABASE_URL=postgresql://user:password@localhost:5432/MinimalPlanner
WEB_URL=http://localhost:3000

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Firebase
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=minibunn-planner
FIREBASE_PRIVATE_KEY_ID=xxx
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nxxx\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@minibunn-planner.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=xxx
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxx@minibunn-planner.iam.gserviceaccount.com

# App-specific
TRIAL_DAYS=14
```

## Local Run

To run the project locally:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

# Test Stripe webhooks
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

## Database Migrations

1. **Autogenerate a migration file**:

   ```bash
   alembic revision --autogenerate -m "Migration description"
   ```

2. **Apply the migration**:

   ```bash
   alembic upgrade head
   ```

3. **View migration history**:

   ```bash
   alembic history
   ```

4. **Downgrade if needed**:

   ```bash
   alembic downgrade -1
   ```

## Testing

- **Reload initial test data**:

  ```bash
  python3 -m app.scripts.init_test_data
  ```

- **Run unit tests**:

  ```bash
  pytest -v
  ```

- **Test Stripe webhooks**:

  ```bash
  stripe listen --forward-to localhost:8000/api/stripe/webhook
  ```

## Release Instructions

1. Create an annotated tag:

   ```bash
   git tag -a v1.0.0 -m "comment"
   git push origin v1.0.0
   ```

2. Draft a GitHub Release:
   - Go to Releases → Draft a new release.
   - Select your new tag.
   - Fill in a “What’s changed” summary or changelog items.
   - Publish.

## Contributing

This repository is public for anyone interested to review the codebase. It is not intended for forks or external contributions. If you have any questions or feedback, please contact the repository owner directly.

## Contact

If you have any advice, comments, or questions about Minibunn Planner API, feel free to reach out:

- **Email**: <contact@minibunnplanner.com>
- **LinkedIn**: <https://www.linkedin.com/company/minibunn-planner>
- **X**: <https://x.com/minibunnplanner>

## License

This project is licensed under a Proprietary License.

### Terms

- The code in this repository is provided for viewing purposes only.
- Copying, modifying, redistributing, or using the code in any form is strictly prohibited.
- For inquiries or permissions, please contact the repository owner directly.

## Frontend Repository

Minibunn Planner also has a frontend repository that handles the user interface and client-side logic. You can find it here:

- [Minibunn Planner Frontend](https://github.com/yangjialin94/minibunn-planner-web)
