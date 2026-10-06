"""Pytest configuration, shared fixtures, database isolation, and test HTTP client."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.webhook as api_webhook
import app.core.database as core_db
from app.api.webhook import ip_rate_limit_cache, last_rate_limit_warning, sender_rate_limit_cache
from app.core.database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

SHARED_MOCK_CATALOG = {
    "product_name": "Warung Makan Sederhana",
    "location": "Jakarta",
    "menus": ["Nasi Goreng", "Mie Goreng"],
    "unique_selling_point": "Porsi kuli harga pelajar",
}


@pytest.fixture(scope="session")
def test_engine():
    """Session-scoped test engine backed by in-memory SQLite."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Session-scoped sessionmaker factory for test database."""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch, test_engine, test_session_factory):
    """Isolates all test runs to an in-memory SQLite database.

    Prevents any mutation to production/development databases.
    """
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()

    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(core_db, "engine", test_engine)
    monkeypatch.setattr(core_db, "SessionLocal", test_session_factory)
    monkeypatch.setattr(api_webhook, "SessionLocal", test_session_factory)
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def reset_rate_limit_caches():
    """Resets webhook rate limit caches before and after each test."""
    sender_rate_limit_cache.clear()
    ip_rate_limit_cache.clear()
    last_rate_limit_warning.clear()
    yield
    sender_rate_limit_cache.clear()
    ip_rate_limit_cache.clear()
    last_rate_limit_warning.clear()


@pytest_asyncio.fixture
async def client():
    """Async test client targeting the FastAPI application."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
