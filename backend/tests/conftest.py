"""Shared pytest fixtures for MusicMate tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.api.deps import get_db
from app.main import app

# Use an in-memory SQLite database for each test session
TEST_DB_URL = "sqlite:///./tests/test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables before tests and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def db_rollback():
    """Roll back each test's changes so tests are isolated."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    app.dependency_overrides[get_db] = lambda: session

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Return a test client with DB override applied."""
    with TestClient(app) as c:
        yield c


# ─── Helper: register + login a user ─────────────────────────────────────────

def register_user(client, suffix="a"):
    email = f"test{suffix}@student.manchester.ac.uk"
    # SSO initiate — returns email, student_id, course, year, faculty (no display_name)
    r = client.post("/api/auth/sso/initiate", json={"email": email})
    assert r.status_code == 200, r.text
    data = r.json()
    # SSO complete
    r2 = client.post("/api/auth/sso/complete", json={
        "email": email,
        "password": "TestPass123!",
        "display_name": f"User {suffix.capitalize()}",
        "student_id": data["student_id"],
        "course": data["course"],
        "year": data["year"],
        "faculty": data["faculty"],
        "show_course": True,
        "show_year": True,
        "show_faculty": True,
    })
    assert r2.status_code == 200, r2.text
    return r2.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
