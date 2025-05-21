import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.deps.auth import get_subscribed_user, get_user
from app.main import app
from app.models.user import User

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared"

# Create a new engine and session for each test
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override FastAPI dependencies
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_user():
    return User(
        id=1,
        firebase_uid="test-firebase-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )


def override_get_subscribed_user():
    return User(
        id=1,
        firebase_uid="test-firebase-uid",
        name="Test User",
        email="test@example.com",
        is_subscribed=True,
    )


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_user] = override_get_user
app.dependency_overrides[get_subscribed_user] = override_get_subscribed_user


# Create tables before running tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)


# Provide a new client for each test
@pytest.fixture
def client():
    # Before each test: clean DB
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


# Create new user for each test
@pytest.fixture
def seeded_client(client):
    db = TestingSessionLocal()
    db.add(
        User(
            id=1,
            firebase_uid="test-firebase-uid",
            name="Test User",
            email="test@example.com",
            is_subscribed=True,
        )
    )
    db.commit()
    db.close()
    return client
