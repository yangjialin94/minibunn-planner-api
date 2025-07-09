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

### Authentication Tests (`test_auth.py`) - 11 tests

#### Unit Tests (7 tests)

- ✅ `test_get_user_success` - Successful user retrieval with valid Firebase token
- ✅ `test_get_user_invalid_token` - Error handling for invalid/expired tokens
- ✅ `test_get_user_not_found` - User not found in database after Firebase validation
- ✅ `test_get_subscribed_user_success` - Successful subscribed user retrieval
- ✅ `test_get_subscribed_user_not_subscribed` - Error for non-subscribed users
- ✅ `test_get_token_firebase_exception` - Firebase token verification exception handling
- ✅ `test_get_token_firebase_exception_http_exception` - Firebase HTTP exception handling

#### Integration Tests (4 tests)

- ✅ `test_protected_endpoint_no_auth` - Access denied without authentication
- ✅ `test_protected_endpoint_invalid_auth` - Access denied with invalid credentials
- ✅ `test_protected_endpoint_valid_auth` - Valid token but user not in database
- ✅ `test_subscription_required_endpoint_no_subscription` - Subscription required endpoints

### Configuration Tests (`test_conftest.py`) - 2 tests

- ✅ `test_conftest_override_functions` - Test fixture dependency override functions
- ✅ `test_conftest_seeded_client_cleanup` - Test client cleanup and isolation

### Database Tests (`test_database.py`) - 8 tests

- ✅ `test_get_db_session_creation` - Database session creation and management
- ✅ `test_get_db_session_cleanup` - Proper session cleanup after use
- ✅ `test_get_db_exception_handling` - Database exception handling
- ✅ `test_sessionlocal_configuration` - Session factory configuration
- ✅ `test_base_declarative_base` - SQLAlchemy base model verification
- ✅ `test_database_connection_properties` - Database connection properties
- ✅ `test_session_transaction_behavior` - Transaction rollback behavior
- ✅ `test_multiple_sessions_independence` - Session isolation verification

### Journal Tests (`test_journals.py`) - 9 tests

- ✅ `test_get_or_create_journal` - Journal creation and retrieval by date
- ✅ `test_post_new_journal_success` - Successful journal creation
- ✅ `test_post_journal_already_exists` - Error handling for duplicate journals
- ✅ `test_patch_journal` - Journal content updates
- ✅ `test_patch_nonexistent_journal` - Error handling for non-existent journals
- ✅ `test_get_or_create_journal_creates_new_empty_journal` - Automatic journal creation
- ✅ `test_patch_journal_with_existing_seeded_client` - Journal updates with seeded data
- ✅ `test_clear_journal_function_directly` - Direct function testing for journal clearing
- ✅ `test_clear_journal_function_not_found` - Error handling for clearing non-existent journals

### Main Application Tests (`test_main.py`) - 2 tests

- ✅ `test_lifespan_context_manager` - Application startup and shutdown lifecycle
- ✅ `test_cors_print_statement` - CORS configuration and print statement coverage

### Notes Tests (`test_notes.py`) - 12 tests

- ✅ `test_create_single_note` - Note creation with proper ordering
- ✅ `test_notes_are_ordered` - Automatic note ordering system
- ✅ `test_update_note_detail` - Note content updates
- ✅ `test_update_note_order` - Note reordering functionality
- ✅ `test_patch_multiple_update_types_fails` - Input validation for conflicting updates
- ✅ `test_delete_note_and_reorder_remaining` - Note deletion and reordering
- ✅ `test_patch_note_not_found` - Error handling for non-existent notes
- ✅ `test_patch_note_order_less_than_one` - Order validation for values less than 1
- ✅ `test_patch_note_order_above_max_gets_clamped` - Order clamping for values above maximum
- ✅ `test_patch_note_reorder_coverage` - Comprehensive reordering logic coverage
- ✅ `test_patch_note_reorder_shift_up_specific` - Specific reordering scenarios
- ✅ `test_delete_note_not_found` - Error handling for deleting non-existent notes

### Scheduler Tests (`test_scheduler.py`) - 5 tests

- ✅ `test_delete_empty_journals_success` - Successful deletion of empty journals
- ✅ `test_delete_empty_journals_database_error` - Database error handling during deletion
- ✅ `test_delete_empty_journals_no_empty_journals` - No action when no empty journals exist
- ✅ `test_start_scheduler` - Scheduler initialization and startup
- ✅ `test_start_scheduler_job_parameters` - Job configuration and parameters verification

### Stripe Integration Tests (`test_stripe.py`) - 21 tests

#### Subscription Status (4 tests)

- ✅ `test_get_subscription_status_no_subscription` - User without subscription
- ✅ `test_get_subscription_status_lifetime` - User with lifetime subscription
- ✅ `test_get_subscription_status_active` - User with active Stripe subscription
- ✅ `test_get_subscription_status_stripe_error` - Stripe API error handling

#### Checkout Sessions (4 tests)

- ✅ `test_create_checkout_session_new_customer` - New customer checkout creation
- ✅ `test_create_checkout_session_existing_customer` - Existing customer checkout
- ✅ `test_create_checkout_session_stripe_customer_error` - Customer creation error handling
- ✅ `test_create_checkout_session_stripe_session_error` - Session creation error handling

#### Subscription Management (3 tests)

- ✅ `test_cancel_subscription_success` - Successful subscription cancellation
- ✅ `test_cancel_subscription_no_subscription` - Error for users without subscription
- ✅ `test_cancel_subscription_stripe_error` - Stripe API error during cancellation

#### Webhook Processing (10 tests)

- ✅ `test_stripe_webhook_checkout_completed_subscription` - Subscription checkout completion
- ✅ `test_stripe_webhook_checkout_completed_payment` - One-time payment completion
- ✅ `test_stripe_webhook_invalid_signature` - Invalid webhook signature handling
- ✅ `test_stripe_webhook_subscription_updated` - Subscription status updates
- ✅ `test_stripe_webhook_subscription_deleted` - Subscription deletion handling
- ✅ `test_stripe_webhook_payment_failed` - Payment failure processing
- ✅ `test_stripe_webhook_invalid_payload` - Invalid webhook payload handling
- ✅ `test_stripe_webhook_invoice_paid` - Invoice payment processing
- ✅ `test_stripe_webhook_unknown_event_type` - Unknown event type handling
- ✅ `test_webhook_unhandled_event_type_with_unknown_customer` - Unhandled events with unknown customer

### Task Management Tests (`test_tasks.py`) - 18 tests

#### Task Creation and Ordering (2 tests)

- ✅ `test_create_single_task` - Basic task creation
- ✅ `test_create_task_inserts_at_beginning` - New tasks inserted at order 1

#### Task Updates (9 tests)

- ✅ `test_patch_multiple_update_types_fails` - Input validation for mixed updates
- ✅ `test_reorder_task_within_day` - Task reordering within the same date
- ✅ `test_update_is_completed_to_incomplete_moves_before_completed` - Completion status updates
- ✅ `test_update_task_date_and_reorder` - Date changes with automatic reordering
- ✅ `test_patch_task_title_and_note_only` - Content-only updates
- ✅ `test_patch_task_with_empty_update_data` - Empty update data handling
- ✅ `test_patch_task_order_validation_zero` - Order validation for zero values
- ✅ `test_patch_task_order_validation_negative` - Order validation for negative values
- ✅ `test_patch_task_reorder_coverage` - Comprehensive reordering logic coverage

#### Task Operations (7 tests)

- ✅ `test_completion_status_route` - Task completion status management
- ✅ `test_get_tasks_within_date_range` - Date range queries
- ✅ `test_delete_task_reorders_remaining` - Task deletion with reordering
- ✅ `test_patch_invalid_order` - Invalid order value handling
- ✅ `test_patch_task_reorder_shift_up_specific` - Specific reordering scenarios
- ✅ `test_delete_task_not_found` - Error handling for deleting non-existent tasks
- ✅ `test_patch_task_not_found` - Error handling for updating non-existent tasks

### User Management Tests (`test_users.py`) - 12 tests

#### User Retrieval (4 tests)

- ✅ `test_get_all_users` - Retrieve all users with related data
- ✅ `test_get_user_by_id_success` - Successful user retrieval by ID
- ✅ `test_get_user_by_id_not_found` - Error handling for non-existent user ID
- ✅ `test_get_current_user_existing` - Current user retrieval for existing user

#### User Creation (2 tests)

- ✅ `test_get_current_user_create_new` - Automatic user creation for new Firebase users
- ✅ `test_get_current_user_create_new_user_debug` - User creation with debug output

#### User Updates (5 tests)

- ✅ `test_patch_user_success` - Successful user profile updates
- ✅ `test_patch_user_not_found` - Error handling for non-existent users
- ✅ `test_patch_user_multiple_fields` - Multiple field updates in single request
- ✅ `test_patch_user_subscription_status` - Subscription status updates
- ✅ `test_patch_user_empty_update` - Empty update data handling

#### Test Infrastructure (1 test)

- ✅ `test_cleanup_override_branch_coverage` - Dependency override cleanup coverage

### Coverage by Component

| Component | Coverage | Status |
|-----------|----------|---------|
| **Models** | 100% | ✅ Excellent |
| **Schemas** | 100% | ✅ Excellent |
| **Task Routes** | 100% | ✅ Excellent |
| **Note Routes** | 100% | ✅ Excellent |
| **Journal Routes** | 100% | ✅ Excellent |
| **User Routes** | 100% | ✅ Excellent |
| **Scheduler** | 100% | ✅ Excellent |
| **Auth Dependencies** | 97% | ✅ Excellent |
| **Main App** | 89% | ✅ Good |
| **Stripe Routes** | 74% | ✅ Good |
| **Database Core** | 100% | ✅ Excellent |
| **Firebase Services** | 100% | ✅ Excellent |

### Test Types

- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test API endpoints with real HTTP requests
- **Mock Tests**: Use mocked external services (Firebase, Stripe) for reliable testing
- **Error Handling Tests**: Validate proper error responses and status codes
- **Input Validation Tests**: Ensure proper request validation and sanitization
- **Edge Case Tests**: Test boundary conditions and unusual scenarios
- **Exception Handling Tests**: Test behavior under error conditions
- **Database Tests**: Test database operations, transactions, and session management
- **Configuration Tests**: Test application setup, fixtures, and dependency injection
- **Lifecycle Tests**: Test application startup, shutdown, and scheduler behavior

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

# Run journal tests only
pytest app/tests/test_journals.py -v

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
| `GET` | `/all` | Get all users with their tasks and journals (testing only) | No |
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

### Journals Routes (`/journals`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/` | Get journal for specific date (creates if doesn't exist) | Subscription |
| `POST` | `/` | Create a new journal entry | Subscription |
| `PATCH` | `/{journal_id}` | Update journal content | Subscription |

### Notes Routes (`/notes`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/` | Get all notes for current user | Subscription |
| `POST` | `/` | Create a new note | Subscription |
| `PATCH` | `/{note_id}` | Update note content or order | Subscription |
| `DELETE` | `/{note_id}` | Delete a note and reorder remaining notes | Subscription |

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
