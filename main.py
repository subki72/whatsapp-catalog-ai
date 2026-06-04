from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.core.database import engine
from app.models import schema
from app.api import webhook, catalog

schema.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp Catalog AI Webhook",
    description="An AI-powered middleware to extract structured catalog JSON from unstructured WA chats.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change "*" to your actual website domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/api/v1", tags=["Webhook"])
app.include_router(catalog.router, prefix="/api/v1/catalogs", tags=["Catalogs"])

# Serve frontend static files (CSS, JS)
frontend_dir = os.path.join(os.path.dirname(__file__), "wa-catalog-frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def root():
    """
    Serve the frontend UI.
    """
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/health")
async def health():
    """
    Health check endpoint to verify the server is running.
    """
    return {
        "status": "online",
        "service": "WhatsApp Catalog AI",
        "message": "Server is up and ready to accept requests."
    }