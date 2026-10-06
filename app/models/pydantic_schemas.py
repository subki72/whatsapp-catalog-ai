"""Pydantic schemas for request validation and AI data exchange."""

import re

from pydantic import BaseModel, Field, field_validator


class CatalogItem(BaseModel):
    """Structured catalog data extracted by the LLM.

    Note: `product_name` holds the business / shop name (e.g. "Kopi Senja");
    individual products and dishes are listed in `menus`.
    """

    product_name: str = Field(description="Business / shop name")
    location: str = Field(
        description=(
            "Business location (e.g. city or address), or 'Tidak disebutkan' if not specified"
        )
    )
    menus: list[str] = Field(description="List of menu items or products offered")
    unique_selling_point: str = Field(
        description="A brief description of what makes this business unique or special"
    )


class WebhookPayload(BaseModel):
    """Pydantic schema for the incoming WhatsApp Payload (e.g. from Fonnte)."""

    sender: str = Field(..., description="Sender phone number (numeric, 8-16 digits)")
    message: str = Field(..., min_length=1, max_length=4096, description="WhatsApp message content")

    @field_validator("sender")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        cleaned = v.strip().lstrip("+")
        if not re.match(r"^\d{8,16}$", cleaned):
            raise ValueError("Sender must be a valid numeric phone number with 8 to 16 digits")
        return cleaned

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Message cannot be empty or whitespace only")
        return cleaned
