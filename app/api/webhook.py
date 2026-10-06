"""WhatsApp webhook endpoints and message background processing."""

import asyncio
import secrets
import time
from collections import defaultdict

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logger import logger
from app.models.pydantic_schemas import WebhookPayload
from app.models.schema import CatalogDB
from app.services.ai_extractor import (
    EMPTY_NAME_VALUES,
    ERROR_TYPE_PARSE,
    ERROR_TYPE_RATE_LIMIT,
    ERROR_TYPE_SERVICE_UNAVAILABLE,
    EXTRACTION_ERROR,
    MISSING_VALUE,
    AIExtractor,
)

router = APIRouter()
extractor = AIExtractor()

sender_rate_limit_cache = defaultdict(list)
ip_rate_limit_cache = defaultdict(list)
last_rate_limit_warning = {}

RATE_LIMIT_MAX_REQUESTS = 3
RATE_LIMIT_WINDOW_SECONDS = 60
IP_RATE_LIMIT_MAX_REQUESTS = 30
IP_RATE_LIMIT_WINDOW_SECONDS = 60

FONNTE_MAX_ATTEMPTS = 2
FONNTE_TIMEOUT_SECONDS = 10.0
FONNTE_RETRY_DELAY_SECONDS = 1.0
CACHE_PRUNE_THRESHOLD = 5000
CACHE_PRUNE_BATCH = 1000

INTERNAL_ERROR_REPLY = (
    "❌ *Kendala Sistem*\n"
    "Maaf, terjadi kendala pada sistem saat memproses katalog Anda. Silakan coba lagi nanti."
)


def get_client_ip(request: Request) -> str | None:
    """Extracts client IP address supporting reverse proxy headers (X-Forwarded-For)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


async def verify_webhook_auth(
    authorization: str | None = Header(None),
    x_webhook_secret: str | None = Header(None, alias="X-Webhook-Secret"),
) -> None:
    """Verifies that the request contains the valid webhook secret if configured.

    Enforces secret requirement in production to avoid open endpoints.
    """
    if not settings.WEBHOOK_SECRET:
        if settings.ENVIRONMENT.lower() == "production":
            logger.error("Webhook secret not configured in production")
            raise HTTPException(
                status_code=500,
                detail=(
                    "Server configuration error: Webhook authentication is required in production."
                ),
            )
        return

    token = None
    if x_webhook_secret:
        token = x_webhook_secret.strip()
    elif authorization:
        scheme, _, param = authorization.strip().partition(" ")
        token = param.strip() if scheme.lower() == "bearer" else authorization.strip()

    if not token or not secrets.compare_digest(token, settings.WEBHOOK_SECRET):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing or invalid webhook secret",
        )


def is_rate_limited(sender: str, client_ip: str | None = None) -> bool:
    """Checks if the sender or client IP has exceeded their request limit.

    Evaluates both dimensions and records non-limited requests.
    """
    current_time = time.time()

    # 1. Evaluate sender limit
    sender_rate_limit_cache[sender] = [
        ts
        for ts in sender_rate_limit_cache[sender]
        if current_time - ts < RATE_LIMIT_WINDOW_SECONDS
    ]
    sender_blocked = len(sender_rate_limit_cache[sender]) >= RATE_LIMIT_MAX_REQUESTS

    # 2. Evaluate client IP limit
    ip_blocked = False
    if client_ip:
        ip_rate_limit_cache[client_ip] = [
            ts
            for ts in ip_rate_limit_cache[client_ip]
            if current_time - ts < IP_RATE_LIMIT_WINDOW_SECONDS
        ]
        ip_blocked = len(ip_rate_limit_cache[client_ip]) >= IP_RATE_LIMIT_MAX_REQUESTS

    if sender_blocked or ip_blocked:
        return True

    sender_rate_limit_cache[sender].append(current_time)
    if client_ip:
        ip_rate_limit_cache[client_ip].append(current_time)

    # Prevent unbounded memory growth over extended runtime
    if len(sender_rate_limit_cache) > CACHE_PRUNE_THRESHOLD:
        empty_senders = [
            sender_key
            for sender_key, timestamps in sender_rate_limit_cache.items()
            if not timestamps
        ]
        for sender_key in empty_senders[:CACHE_PRUNE_BATCH]:
            sender_rate_limit_cache.pop(sender_key, None)

    if len(ip_rate_limit_cache) > CACHE_PRUNE_THRESHOLD:
        empty_ips = [
            client_ip_key
            for client_ip_key, timestamps in ip_rate_limit_cache.items()
            if not timestamps
        ]
        for client_ip_key in empty_ips[:CACHE_PRUNE_BATCH]:
            ip_rate_limit_cache.pop(client_ip_key, None)

    return False


async def send_whatsapp_reply(phone_number: str, text: str) -> None:
    """Sends a reply message to the target WhatsApp number via Fonnte gateway with retry."""
    if not settings.FONNTE_TOKEN:
        logger.info(
            "Simulated Fonnte API dispatch to target=%s: %s",
            phone_number,
            text,
        )
        return

    headers = {"Authorization": settings.FONNTE_TOKEN}
    data = {"target": phone_number, "message": text}

    for attempt in range(1, FONNTE_MAX_ATTEMPTS + 1):
        try:
            async with httpx.AsyncClient(timeout=FONNTE_TIMEOUT_SECONDS) as client:
                response = await client.post(settings.FONNTE_API_URL, headers=headers, data=data)
                if response.is_success:
                    logger.info("WhatsApp reply sent successfully to %s", phone_number)
                    return
                logger.warning(
                    "Fonnte API attempt %d returned status %s: %s",
                    attempt,
                    response.status_code,
                    response.text,
                )
        except Exception as exc:
            logger.warning("Fonnte API attempt %d failed: %s", attempt, exc)

        if attempt < FONNTE_MAX_ATTEMPTS:
            await asyncio.sleep(FONNTE_RETRY_DELAY_SECONDS)

    logger.error(
        "Failed to dispatch WhatsApp reply to %s after %d attempts",
        phone_number,
        FONNTE_MAX_ATTEMPTS,
    )


def is_extraction_error(extracted_data: dict) -> bool:
    """Checks whether the AI extraction result indicates an error."""
    return extracted_data.get("product_name") == EXTRACTION_ERROR or bool(
        extracted_data.get("error_type")
    )


def build_extraction_error_reply(extracted_data: dict) -> str:
    """Builds a user-friendly WhatsApp error message for extraction failures."""
    error_type = extracted_data.get("error_type", "")
    usp = extracted_data.get("unique_selling_point", "")

    if error_type in {ERROR_TYPE_SERVICE_UNAVAILABLE, ERROR_TYPE_RATE_LIMIT}:
        return (
            "⚠️ *Layanan AI Sibuk*\n"
            "Maaf, sistem AI kami sedang sibuk atau mengalami kendala teknis. "
            "Mohon coba kirimkan kembali pesan Anda dalam beberapa saat."
        )
    if error_type == ERROR_TYPE_PARSE:
        return (
            "❌ *Gagal Memproses Katalog*\n"
            "Maaf, AI belum berhasil memahami data jualan Anda. Silakan coba lagi "
            "dengan menyertakan nama usaha, lokasi, dan daftar menu yang jelas."
        )

    # Heuristic fallback for legacy error payloads without error_type
    if any(token in usp.lower() for token in ("system", "limit", "busy")):
        return (
            "⚠️ *Layanan AI Sibuk*\n"
            "Maaf, sistem AI kami sedang sibuk atau mengalami kendala teknis. "
            "Mohon coba kirimkan kembali pesan Anda dalam beberapa saat."
        )
    return (
        "❌ *Gagal Memproses Katalog*\n"
        "Maaf, AI belum berhasil memahami data jualan Anda. Silakan coba lagi "
        "dengan menyertakan nama usaha, lokasi, dan daftar menu yang jelas."
    )


def build_success_reply(catalog: CatalogDB, sender: str) -> str:
    """Builds a formatted WhatsApp confirmation reply for a saved catalog."""
    return (
        f"✅ *Katalog Berhasil Disimpan!*\n\n"
        f"🛍 Nama Usaha: {catalog.product_name}\n"
        f"📍 Lokasi: {catalog.location}\n"
        f"💡 Keunggulan: {catalog.unique_selling_point}\n\n"
        f"Akses link etalase katalog Anda di: {settings.APP_BASE_URL}/users/{sender}/catalogs"
    )


def upsert_catalog(db: Session, sender: str, extracted_data: dict) -> tuple[CatalogDB, bool]:
    """Inserts or updates a catalog entry in the database.

    Returns the catalog instance and a boolean indicating whether it was an update.
    """
    business_name = extracted_data.get("product_name", "").strip()
    is_name_missing = business_name.lower() in EMPTY_NAME_VALUES or not business_name

    # Match existing catalog for this sender by business name (case-insensitive)
    existing_catalog = None
    if not is_name_missing:
        existing_catalog = (
            db.query(CatalogDB)
            .filter(
                CatalogDB.user_id == sender,
                func.lower(CatalogDB.product_name) == business_name.lower(),
            )
            .first()
        )

    # If business name was not provided, fallback to the user's existing catalog if any
    if not existing_catalog and is_name_missing:
        existing_catalog = (
            db.query(CatalogDB)
            .filter(CatalogDB.user_id == sender)
            .order_by(CatalogDB.updated_at.desc(), CatalogDB.id.desc())
            .first()
        )

    if existing_catalog:
        if not is_name_missing:
            existing_catalog.product_name = business_name

        new_location = extracted_data.get("location", "").strip()
        if new_location and new_location.lower() not in EMPTY_NAME_VALUES:
            existing_catalog.location = new_location

        new_menus = extracted_data.get("menus", [])
        if new_menus:
            existing_catalog.menus = new_menus

        new_usp = extracted_data.get("unique_selling_point", "").strip()
        if new_usp and new_usp.lower() not in EMPTY_NAME_VALUES:
            existing_catalog.unique_selling_point = new_usp

        existing_catalog.updated_at = func.now()
        catalog = existing_catalog
        is_update = True
    else:
        new_catalog = CatalogDB(
            user_id=sender,
            product_name=business_name if not is_name_missing else MISSING_VALUE,
            location=extracted_data.get("location", "") or MISSING_VALUE,
            menus=extracted_data.get("menus", []),
            unique_selling_point=extracted_data.get("unique_selling_point", ""),
        )
        db.add(new_catalog)
        catalog = new_catalog
        is_update = False

    db.commit()
    db.refresh(catalog)
    return catalog, is_update


async def background_process_wa_message(sender: str, message: str) -> None:
    """Background task: extracts catalog data, upserts into DB, and replies via WhatsApp."""
    try:
        logger.info("Processing background message from sender=%s", sender)
        extracted_data = await extractor.extract_catalog_data(message)

        if is_extraction_error(extracted_data):
            logger.warning("AI extraction failed for sender=%s: %s", sender, extracted_data)
            await send_whatsapp_reply(sender, build_extraction_error_reply(extracted_data))
            return

        db = SessionLocal()
        try:
            catalog, is_update = upsert_catalog(db, sender, extracted_data)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        action = "UPDATED" if is_update else "CREATED"
        logger.info("Successfully %s catalog ID %s for sender=%s", action, catalog.id, sender)
        await send_whatsapp_reply(sender, build_success_reply(catalog, sender))

    except Exception as exc:
        logger.error(
            "Webhook background processing error for sender=%s: %s",
            sender,
            exc,
            exc_info=True,
        )
        await send_whatsapp_reply(sender, INTERNAL_ERROR_REPLY)


@router.post("/whatsapp-catalog")
async def process_whatsapp_message(
    payload: WebhookPayload,
    request: Request,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_webhook_auth),
) -> dict:
    """Receives WhatsApp message webhook from Fonnte.

    Immediately returns 200 OK so Fonnte does not timeout.
    Enforces rate limiting per sender and client IP.
    """
    client_ip = get_client_ip(request)
    if is_rate_limited(payload.sender, client_ip):
        logger.warning(
            "Rate limit exceeded for sender=%s from ip=%s",
            payload.sender,
            client_ip,
        )

        current_time = time.time()
        time_since_warning = current_time - last_rate_limit_warning.get(payload.sender, 0)
        # Throttled warning reply: only at most 1 warning message per window
        if time_since_warning >= RATE_LIMIT_WINDOW_SECONDS:
            last_rate_limit_warning[payload.sender] = current_time
            wait_minutes = RATE_LIMIT_WINDOW_SECONDS // 60 or 1
            warning_msg = (
                f"⚠️ *Batas Pengiriman Terlampaui*\n"
                f"Mohon tunggu {wait_minutes} menit sebelum mencoba lagi."
            )
            background_tasks.add_task(
                send_whatsapp_reply,
                payload.sender,
                warning_msg,
            )
        return {
            "status": "error",
            "message": f"Rate limit exceeded (Max {RATE_LIMIT_MAX_REQUESTS} per minute).",
        }

    background_tasks.add_task(background_process_wa_message, payload.sender, payload.message)

    return {
        "status": "success",
        "message": "Webhook received; processing in background.",
    }
