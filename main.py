"""FastAPI application entry point, middleware configuration, and core routing."""

import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api import catalog, webhook
from app.core.config import settings
from app.core.database import engine, get_db
from app.core.logger import logger
from app.core.migrations import run_migrations
from app.models import schema

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "wa-catalog-frontend")
INDEX_FILE = os.path.join(FRONTEND_DIR, "index.html")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown lifecycle events."""
    schema.Base.metadata.create_all(bind=engine)
    run_migrations(engine)
    yield


app = FastAPI(
    title="WhatsApp Catalog AI Webhook",
    description=(
        "An AI-powered middleware to extract structured catalog JSON from unstructured WA chats."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that injects secure HTTP headers into every outgoing response."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Secure CORS Middleware
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
allow_all = not origins or origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/api/v1", tags=["Webhook"])
app.include_router(catalog.router, prefix="/api/v1/catalogs", tags=["Catalogs"])

# Serve frontend static files (CSS, JS)
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root() -> Response:
    """Serve the frontend UI."""
    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return JSONResponse(status_code=404, content={"detail": "Frontend not found"})


@app.get("/users/{user_id}/catalogs")
async def user_catalog_page(user_id: str) -> Response:
    """Serve the frontend catalog UI for a specific merchant.

    Allows WhatsApp confirmation links to open directly in the browser.
    """
    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return JSONResponse(status_code=404, content={"detail": "Frontend not found"})


@app.get("/health")
def health(db: Session = Depends(get_db)) -> Response:
    """Health check endpoint verifying database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "database": "connected",
                "service": "WhatsApp Catalog AI",
            },
        )
    except Exception as exc:
        logger.error("Health check database failure: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "service": "WhatsApp Catalog AI",
                "error": str(exc),
            },
        )
