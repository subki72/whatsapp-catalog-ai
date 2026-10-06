"""SQLAlchemy ORM models representing database tables."""

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class CatalogDB(Base):
    """A merchant catalog entry in the 'catalogs' database table.

    Note: `product_name` stores the business / shop name (e.g. "Kopi Senja");
    individual menu items and dishes are stored in `menus`.
    """

    __tablename__ = "catalogs"

    id = Column(Integer, primary_key=True, index=True)
    # WhatsApp phone number in international format without "+" (e.g. "6281234567890")
    user_id = Column(String, index=True)
    # Business / shop name
    product_name = Column(String, index=True)
    location = Column(String)

    # JSON column to store the menu list directly without a separate table
    menus = Column(JSON)

    unique_selling_point = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
