# Minibunn Planner (API)

Minibunn Planner API is the backend service for the Minibunn Planner application. It provides server-side logic, database management, and APIs for tasks, backlogs, notes, calendars, and user management. This repository is public to allow anyone interested to review the codebase and understand the project's structure and implementation. It is not intended for forks or external contributions.

## Features

- **Task Management**: APIs for creating, updating, and managing tasks.
- **Backlogs**: APIs for creating and organizing backlog items.
- **Notes**: APIs for maintaining daily notes.
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

- **Run tests with coverage**:

  ```bash
  pytest --cov=app --cov-report=term-missing
  ```

- **Test Stripe webhooks**:

  ```bash
  stripe listen --forward-to localhost:8000/api/stripe/webhook
  ```

## Test Cases

The API has comprehensive test coverage with **102 tests** across all major functionalities, achieving **97% code coverage**. The test suite includes both unit tests and integration tests to ensure reliability and maintainability.

### Test Statistics

- **Total Tests**: 102
- **Pass Rate**: 100% ✅
- **Code Coverage**: 97%
- **Test Files**: 11

### Coverage by Component

| Component | Coverage | Status |
|-----------|----------|---------|
| **Models** | 100% | ✅ Excellent |
| **Schemas** | 100% | ✅ Excellent |
| **Task Routes** | 100% | ✅ Excellent |
| **Backlog Routes** | 100% | ✅ Excellent |
| **Note Routes** | 100% | ✅ Excellent |
| **User Routes** | 100% | ✅ Excellent |
| **Scheduler** | 100% | ✅ Excellent |
| **Auth Dependencies** | 97% | ✅ Excellent |
| **Main App** | 89% | ✅ Good |
| **Stripe Routes** | 74% | ✅ Good |
| **Database Core** | 100% | ✅ Excellent |
| **Firebase Services** | 100% | ✅ Excellent |

### Running Specific Test Suites

```bash
# Run authentication tests only
pytest app/tests/test_auth.py -v

# Run Stripe integration tests only
pytest app/tests/test_stripe.py -v

# Run task management tests only
pytest app/tests/test_tasks.py -v

# Run note management tests only
pytest app/tests/test_notes.py -v

# Run backlog management tests only
pytest app/tests/test_backlogs.py -v

# Run user management tests only
pytest app/tests/test_users.py -v

# Run database tests only
pytest app/tests/test_database.py -v

# Run scheduler tests only
pytest app/tests/test_scheduler.py -v

# Run configuration tests only
pytest app/tests/test_conftest.py -v

# Run main application tests only
pytest app/tests/test_main.py -v

# Run with coverage for specific module
pytest app/tests/test_stripe.py --cov=app.routes.stripe --cov-report=term-missing

# Run tests in parallel for faster execution
pytest -n auto

# Run all tests with verbose coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing
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

## API Routes

The Minibunn Planner API provides the following endpoints:

### Users Routes (`/users`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/all` | Get all users with their tasks, notes, and backlogs (testing only) | No |
| `GET` | `/by_id/{user_id}` | Get a specific user by ID with their data (testing only) | No |
| `GET` | `/get_current` | Get current user or create if doesn't exist | Firebase Token |
| `PATCH` | `/{user_id}` | Update user information | Subscription |

### Tasks Routes (`/tasks`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/` | Get tasks for current user (optional date range) | Firebase Token |
| `POST` | `/` | Create a new task | Firebase Token |
| `PATCH` | `/{task_id}` | Update task (order, completion, content, or date) | Firebase Token |
| `DELETE` | `/{task_id}` | Delete a task and reorder remaining tasks | Firebase Token |
| `GET` | `/completion/` | Get completion statistics for date range | Firebase Token |

### Notes Routes (`/notes`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/` | Get note for specific date (creates if doesn't exist) | Subscription |
| `POST` | `/` | Create a new note entry | Subscription |
| `PATCH` | `/{note_id}` | Update note content | Subscription |

### Backlogs Routes (`/backlogs`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/` | Get all backlogs for current user | Subscription |
| `POST` | `/` | Create a new backlog | Subscription |
| `PATCH` | `/{backlog_id}` | Update backlog content or order | Subscription |
| `DELETE` | `/{backlog_id}` | Delete a backlog and reorder remaining backlogs | Subscription |

### Stripe Routes (`/stripe`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/subscription-status` | Get current subscription status | Firebase Token |
| `POST` | `/create-checkout-session` | Create Stripe checkout session | Firebase Token |
| `POST` | `/cancel-subscription` | Cancel active subscription | Subscription |
| `POST` | `/webhook` | Handle Stripe webhook events | Webhook Signature |

### Authentication Levels

- **No Auth**: Public endpoints (testing/development only)
- **Firebase Token**: Requires valid Firebase authentication token
- **Subscription**: Requires Firebase token + active subscription
- **Webhook Signature**: Requires valid Stripe webhook signature

### Common Response Formats

All endpoints return JSON responses with appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (missing/invalid token)
- `403`: Forbidden (subscription required)
- `404`: Not Found
- `422`: Unprocessable Entity (schema validation)
- `500`: Internal Server Error

Error responses include a `detail` field with the error message.

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
