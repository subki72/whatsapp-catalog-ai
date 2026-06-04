from pydantic import BaseModel, Field
from typing import List, Optional

class CatalogItem(BaseModel):
    """
    Pydantic schema for LangChain to parse the extracted AI data.
    """
    product_name: str = Field(description="Name of the product or business")
    location: str = Field(description="Location of the business, or 'Not provided' if not found")
    menus: List[str] = Field(description="List of menu items or products offered")
    unique_selling_point: str = Field(description="A brief description of what makes this business unique or special")

class WebhookPayload(BaseModel):
    """
    Pydantic schema for the incoming WhatsApp Payload (e.g. from Fonnte).
    """
    sender: str
    message: str
