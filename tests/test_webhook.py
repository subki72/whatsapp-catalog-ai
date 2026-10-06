"""Tests for webhook authentication, IP rate limiting, outbound replies, and background tasks."""

import pytest

import app.core.database as core_db
from app.api.webhook import background_process_wa_message, send_whatsapp_reply
from app.core.config import settings
from app.models.schema import CatalogDB
from tests.conftest import SHARED_MOCK_CATALOG


@pytest.mark.asyncio
async def test_webhook_unauthorized_when_secret_configured(client, monkeypatch, mocker):
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value=SHARED_MOCK_CATALOG,
    )
    monkeypatch.setattr(settings, "WEBHOOK_SECRET", "super-secret-key")

    payload = {
        "sender": "6281234567890",
        "message": "Mau buat katalog usaha Warung Bakso",
    }

    # Without auth header
    res_no_auth = await client.post("/api/v1/whatsapp-catalog", json=payload)
    assert res_no_auth.status_code == 401

    # With wrong auth header
    res_wrong_auth = await client.post(
        "/api/v1/whatsapp-catalog",
        json=payload,
        headers={"X-Webhook-Secret": "wrong-secret"},
    )
    assert res_wrong_auth.status_code == 401

    # With correct auth header
    res_valid = await client.post(
        "/api/v1/whatsapp-catalog",
        json=payload,
        headers={"X-Webhook-Secret": "super-secret-key"},
    )
    assert res_valid.status_code == 200


@pytest.mark.asyncio
async def test_webhook_bearer_token_auth(client, monkeypatch, mocker):
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value=SHARED_MOCK_CATALOG,
    )
    monkeypatch.setattr(settings, "WEBHOOK_SECRET", "my-bearer-token")

    payload = {
        "sender": "6281234567890",
        "message": "Katalog Kopi Senja",
    }

    res = await client.post(
        "/api/v1/whatsapp-catalog",
        json=payload,
        headers={"Authorization": "Bearer my-bearer-token"},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_webhook_invalid_phone_validation(client):
    invalid_payloads = [
        {"sender": "invalid-phone", "message": "Test"},
        {"sender": "123", "message": "Too short"},
        {"sender": "62812345678901234567890", "message": "Too long"},
    ]

    for payload in invalid_payloads:
        res = await client.post("/api/v1/whatsapp-catalog", json=payload)
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_webhook_empty_and_oversized_message_validation(client):
    # Empty message
    res_empty = await client.post(
        "/api/v1/whatsapp-catalog",
        json={"sender": "6281234567890", "message": "   "},
    )
    assert res_empty.status_code == 422

    # Oversized message (> 4096 chars)
    res_oversized = await client.post(
        "/api/v1/whatsapp-catalog",
        json={"sender": "6281234567890", "message": "a" * 4097},
    )
    assert res_oversized.status_code == 422


@pytest.mark.asyncio
async def test_webhook_production_fails_when_secret_unset(client, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "WEBHOOK_SECRET", "")

    res = await client.post(
        "/api/v1/whatsapp-catalog",
        json={"sender": "6281234567890", "message": "Hello"},
    )
    assert res.status_code == 500
    assert "Server configuration error" in res.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_ip_rate_limiting(client, mocker):
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value=SHARED_MOCK_CATALOG,
    )

    client_ip = "198.51.100.42"
    headers = {"X-Forwarded-For": client_ip}

    # Send 30 requests with unique sender IDs from the same IP
    for i in range(30):
        payload = {"sender": f"628120000{i:04d}", "message": f"Test message {i}"}
        res = await client.post("/api/v1/whatsapp-catalog", json=payload, headers=headers)
        assert res.status_code == 200
        assert res.json()["status"] == "success"

    # 31st request with a fresh sender ID must be blocked by IP rate limit
    res_blocked = await client.post(
        "/api/v1/whatsapp-catalog",
        json={"sender": "6281999999999", "message": "Blocked by IP"},
        headers=headers,
    )
    assert res_blocked.status_code == 200
    assert res_blocked.json()["status"] == "error"


@pytest.mark.asyncio
async def test_outbound_whatsapp_reply_with_http_retry(monkeypatch, mocker):
    monkeypatch.setattr(settings, "FONNTE_TOKEN", "valid-fonnte-token")

    mock_resp_fail = mocker.MagicMock(
        is_success=False, status_code=500, text="Internal Server Error"
    )
    mock_resp_ok = mocker.MagicMock(is_success=True, status_code=200, text="OK")

    post_mock = mocker.AsyncMock(side_effect=[mock_resp_fail, mock_resp_ok])
    mocker.patch("httpx.AsyncClient.post", post_mock)

    await send_whatsapp_reply("6281234567890", "Test Reply")
    assert post_mock.call_count == 2


@pytest.mark.asyncio
async def test_background_process_wa_message_ai_error(mocker):
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value={
            "product_name": "Error",
            "location": "Error",
            "menus": [],
            "unique_selling_point": "System rate limit",
            "error_type": "rate_limit",
        },
    )
    reply_mock = mocker.patch("app.api.webhook.send_whatsapp_reply", mocker.AsyncMock())

    await background_process_wa_message("6281234567890", "Random text")
    assert reply_mock.called
    assert "sedang sibuk" in reply_mock.call_args[0][1]


@pytest.mark.asyncio
async def test_same_sender_can_own_multiple_catalogs(mocker):
    sender = "628777888999"
    mocker.patch("app.api.webhook.send_whatsapp_reply", mocker.AsyncMock())

    # First business
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value={
            "product_name": "Warung Bakso Enak",
            "location": "Malang",
            "menus": ["Bakso"],
            "unique_selling_point": "Daging sapi asli",
        },
    )
    await background_process_wa_message(sender, "Bikin katalog Warung Bakso Enak")

    # Second business for same sender
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value={
            "product_name": "Kopi Senja Bahagia",
            "location": "Malang",
            "menus": ["Es Kopi"],
            "unique_selling_point": "Tempat estetik",
        },
    )
    await background_process_wa_message(sender, "Bikin katalog Kopi Senja Bahagia")

    db = core_db.SessionLocal()
    try:
        user_catalogs = db.query(CatalogDB).filter(CatalogDB.user_id == sender).all()
        assert len(user_catalogs) == 2
        names = {c.product_name for c in user_catalogs}
        assert "Warung Bakso Enak" in names
        assert "Kopi Senja Bahagia" in names
    finally:
        db.close()


@pytest.mark.asyncio
async def test_background_process_wa_message_parse_error(mocker):
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value={
            "product_name": "Error",
            "location": "Error",
            "menus": [],
            "unique_selling_point": "Invalid text format",
            "error_type": "parse_error",
        },
    )
    reply_mock = mocker.patch("app.api.webhook.send_whatsapp_reply", mocker.AsyncMock())

    await background_process_wa_message("6281234567890", "Text that could not be parsed")
    assert reply_mock.called
    reply_text = reply_mock.call_args[0][1]
    assert "Gagal Memproses Katalog" in reply_text
    assert "nama usaha" in reply_text


@pytest.mark.asyncio
async def test_background_process_wa_message_sentinel_fallback(mocker):
    sender = "62811223344"
    reply_mock = mocker.patch("app.api.webhook.send_whatsapp_reply", mocker.AsyncMock())

    # Create initial catalog
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value={
            "product_name": "Kedai Kopi Asli",
            "location": "Jakarta",
            "menus": ["Kopi Hitam"],
            "unique_selling_point": "Rasa mantap",
        },
    )
    await background_process_wa_message(sender, "Bikin katalog Kedai Kopi Asli")

    # Update with sentinel business name
    mocker.patch(
        "app.services.ai_extractor.AIExtractor.extract_catalog_data",
        return_value={
            "product_name": "Tidak disebutkan",
            "location": "Jakarta Selatan",
            "menus": ["Kopi Hitam", "Kopi Susu"],
            "unique_selling_point": "Rasa lebih mantap",
        },
    )
    await background_process_wa_message(sender, "Update menu tambah kopi susu")

    db = core_db.SessionLocal()
    try:
        user_catalogs = db.query(CatalogDB).filter(CatalogDB.user_id == sender).all()
        assert len(user_catalogs) == 1
        assert user_catalogs[0].product_name == "Kedai Kopi Asli"
        assert user_catalogs[0].location == "Jakarta Selatan"
        assert len(user_catalogs[0].menus) == 2
        assert user_catalogs[0].unique_selling_point == "Rasa lebih mantap"
    finally:
        db.close()
    assert reply_mock.called
    latest_reply = reply_mock.call_args_list[-1][0][1]
    assert "Kedai Kopi Asli" in latest_reply
    assert "Tidak disebutkan" not in latest_reply
