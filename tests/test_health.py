"""Tests for healthcheck and root frontend serving endpoints."""

import pytest

from app.core.database import get_db
from main import app


@pytest.mark.asyncio
async def test_health_success(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["service"] == "WhatsApp Catalog AI"


@pytest.mark.asyncio
async def test_health_db_failure(client):
    def broken_get_db():
        class FailingSession:
            def execute(self, query):
                raise RuntimeError("Connection dropped")

            def close(self):
                pass

        yield FailingSession()

    app.dependency_overrides[get_db] = broken_get_db
    try:
        response = await client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
