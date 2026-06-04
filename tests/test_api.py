import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.api.webhook import rate_limit_cache


MOCK_EXTRACTED_DATA = {
    "product_name": "Warung Makan Sederhana",
    "location": "Jakarta",
    "menus": ["Nasi Goreng", "Mie Goreng"],
    "unique_selling_point": "Porsi kuli harga pelajar"
}

@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Reset rate limit cache before every test execution."""
    rate_limit_cache.clear()
    yield

@pytest.mark.asyncio
async def test_webhook_success(mocker):
    """
    Test standard incoming Webhook successfully initiates 
    business logic and returns 200 without waiting for AI.
    """
    mocker.patch(
        'app.services.ai_extractor.AIExtractor.extract_catalog_data',
        return_value=MOCK_EXTRACTED_DATA
    )

    payload = {
        "sender": "6281111111",
        "message": "Tolong bantu buatin katalog jualan saya Warung Makan Sederhana di Jakarta"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/whatsapp-catalog", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Webhook received, data processing heavily in background."
    }

@pytest.mark.asyncio
async def test_webhook_rate_limit(mocker):
    """
    Test Anti-Spam protection: 4th message within a minute from 
    the same sender should be rate-limited and logged.
    """
    mocker.patch(
        'app.services.ai_extractor.AIExtractor.extract_catalog_data',
        return_value=MOCK_EXTRACTED_DATA
    )
    
    sender_number = "6289999999"
    payload = {
        "sender": sender_number,
        "message": "Spam message test"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Send 3 requests to exhaust the rate limit
        for _ in range(3):
            res = await ac.post("/api/v1/whatsapp-catalog", json=payload)
            assert res.status_code == 200
            assert res.json()["status"] == "success"
        
        # 4th request should be rate-limited
        res = await ac.post("/api/v1/whatsapp-catalog", json=payload)
        assert res.status_code == 200
        assert res.json() == {
            "status": "error",
            "message": "Rate limit exceeded (Max 3 per minute)."
        }
