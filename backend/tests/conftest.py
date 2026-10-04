import os

# Must be set before the app is imported: auth_utils refuses to start without a secret,
# and the chat agent builds its OpenAI client at import time (no calls are made in tests).
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHAT_CHECKPOINTER", "memory")  # never touch the real Postgres from tests

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.auth_utils import create_access_token, hash_password  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402
from app.rate_limit import limiter  # noqa: E402


@pytest.fixture
def db_session():
    # StaticPool keeps one connection, so the in-memory DB is shared with the TestClient's thread
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    limiter.reset()  # rate-limit counters are global; start every test from zero
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db_session):
    def _make_user(email: str, role: str = "citizen") -> User:
        user = User(email=email, name=email.split("@")[0], hashed_password=hash_password("Password123"), role=role)
        db_session.add(user)
        db_session.commit()
        return user
    return _make_user


def auth_header(user: User) -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user.id)})}"}
