from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import requests
import time
from collections import defaultdict

from app.services.ai_extractor import AIExtractor
from app.core.database import SessionLocal
from app.models.schema import CatalogDB
from app.models.pydantic_schemas import WebhookPayload
from app.core.logger import logger

router = APIRouter()
extractor = AIExtractor()

rate_limit_cache = defaultdict(list)
RATE_LIMIT_MAX_REQUESTS = 3
RATE_LIMIT_WINDOW_SECONDS = 60

def is_rate_limited(sender: str) -> bool:
    """
    Checks if the sender has exceeded 3 requests per minute.
    Returns True if rate limited, False otherwise.
    """
    current_time = time.time()
    
    rate_limit_cache[sender] = [
        ts for ts in rate_limit_cache[sender] 
        if current_time - ts < RATE_LIMIT_WINDOW_SECONDS
    ]
    
    if len(rate_limit_cache[sender]) >= RATE_LIMIT_MAX_REQUESTS:
        return True
        
    rate_limit_cache[sender].append(current_time)
    return False

def send_whatsapp_reply(target_number: str, text: str):
    """
    Send a reply message to the user via WhatsApp provider (Fonnte).
    Replace the token and URL below according to your Fonnte account.
    """
    url = "https://api.fonnte.com/send"
    headers = {
        "Authorization": "YOUR_FONNTE_TOKEN_HERE"
    }
    data = {
        "target": target_number,
        "message": text
    }
    
    
    logger.info(f"\n[Simulated Fonnte API] Sending WhatsApp to {target_number}: \n{text}\n")


async def background_process_wa_message(sender: str, message: str):
    """
    Background process: Calls AI for data extraction, saves it to the DB, 
    and responds to the user via Fonnte API.
    """
    try:
        logger.info(f"Background Task: Processing message from {sender}...")
        extracted_data = await extractor.extract_catalog_data(message)
        
        if extracted_data.get("product_name") == "Error":
             logger.warning(f"AI Extraction failed for {sender}: {extracted_data}")
             send_whatsapp_reply(sender, "Sorry, the AI failed to process your sales data. Please try again with a clearer description.")
             return
             
        db = SessionLocal()
        try:
            # Upsert: check if this sender already has an existing catalog
            existing_catalog = db.query(CatalogDB).filter(CatalogDB.user_id == sender).first()
            
            if existing_catalog:
                # UPDATE: overwrite existing catalog with new data
                existing_catalog.product_name = extracted_data["product_name"]
                existing_catalog.location = extracted_data["location"]
                existing_catalog.menus = extracted_data["menus"]
                existing_catalog.unique_selling_point = extracted_data["unique_selling_point"]
                catalog = existing_catalog
                logger.info(f"Successfully UPDATED catalog ID {catalog.id} to database.")
            else:
                # INSERT: create new catalog entry for first-time sender
                new_catalog = CatalogDB(
                    user_id=sender,
                    product_name=extracted_data["product_name"],
                    location=extracted_data["location"],
                    menus=extracted_data["menus"],
                    unique_selling_point=extracted_data["unique_selling_point"]
                )
                db.add(new_catalog)
                catalog = new_catalog
                logger.info(f"Successfully CREATED new catalog ID {catalog.id} to database.")

            db.commit()
            db.refresh(catalog)
            
            reply_text = (
                f"✅ *Catalog Successfully Saved!*\n\n"
                f"🛍 Business Name: {catalog.product_name}\n"
                f"📍 Location: {catalog.location}\n"
                f"💡 Unique Point: {catalog.unique_selling_point}\n\n"
                f"Please access your application link at: https://app.mynamedomain.com/users/{sender}/catalogs"
            )
            send_whatsapp_reply(sender, reply_text)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Webhook Background Error: {e}", exc_info=True)
        send_whatsapp_reply(sender, "The system encountered an internal error while processing AI data.")

@router.post("/whatsapp-catalog")
async def process_whatsapp_message(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Receives WhatsApp message from Fonnte.
    Immediately returns 200 OK so Fonnte doesn't timeout.
    Enforces Rate Limiting per sender.
    """
    if is_rate_limited(payload.sender):
        logger.warning(f"SPAM BLOCKED: Rate limit exceeded for {payload.sender}")
        
        background_tasks.add_task(
            send_whatsapp_reply, 
            payload.sender, 
            "⚠️ You are sending requests too fast. Please wait 1 minute before trying again."
        )
        return {
            "status": "error",
            "message": "Rate limit exceeded (Max 3 per minute)."
        }

    background_tasks.add_task(background_process_wa_message, payload.sender, payload.message)
    
    return {
        "status": "success",
        "message": "Webhook received, data processing heavily in background."
    }