from sqlalchemy import Column, Integer, String, Text, JSON
from app.core.database import Base

class CatalogDB(Base):

    __tablename__ = "catalogs"


    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    product_name = Column(String, index=True)
    location = Column(String)
    
    # JSON column to store the menu list directly without a separate table
    menus = Column(JSON) 
    
    unique_selling_point = Column(Text)