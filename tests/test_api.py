"""Tests for webhook endpoints, rate limiting, and response contracts."""

import pytest

from tests.conftest import SHARED_MOCK_CATALOG


@pytest.mark.asyncio
async def test_webhook_success(client, mocker):
    """Test standard incoming Webhook initiates background processing and returns 200."""
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value=SHARED_MOCK_CATALOG,
    )

    payload = {
        "sender": "6281111111",
        "message": "Tolong bantu buatin katalog jualan saya Warung Makan Sederhana di Jakarta",
    }

    response = await client.post("/api/v1/whatsapp-catalog", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Webhook received; processing in background.",
    }


@pytest.mark.asyncio
async def test_webhook_rate_limit(client, mocker):
    """Test Anti-Spam protection: 4th message within a minute from same sender is rate-limited."""
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value=SHARED_MOCK_CATALOG,
    )

    sender_number = "6289999999"
    payload = {
        "sender": sender_number,
        "message": "Spam message test",
    }

    # Send 3 requests to exhaust the rate limit
    for _ in range(3):
        res = await client.post("/api/v1/whatsapp-catalog", json=payload)
        assert res.status_code == 200
        assert res.json()["status"] == "success"

    # 4th request should be rate-limited
    res = await client.post("/api/v1/whatsapp-catalog", json=payload)
    assert res.status_code == 200
    assert res.json() == {
        "status": "error",
        "message": "Rate limit exceeded (Max 3 per minute).",
    }
