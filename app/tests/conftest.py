import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.deps.auth import get_user_id
from app.main import app

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


def override_get_user_id():
    return 1  # consistent test user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_user_id] = override_get_user_id


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
