from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import random

from app.core.database import get_db
from app.models.schema import CatalogDB

router = APIRouter()

@router.get("/")
async def get_all_catalogs(db: Session = Depends(get_db)):
    """
    Fetch all catalog items across all users (Homepage).
    Returns the items in a randomized order.
    """
    try:
        catalogs = db.query(CatalogDB).all()
        random.shuffle(catalogs)
        
        return {
            "status": "success",
            "total_items": len(catalogs),
            "data": catalogs
        }
    except Exception as e:
        print(f"Database Fetch Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}/catalogs")
async def get_user_catalogs(user_id: str, db: Session = Depends(get_db)):
    """
    Fetch all catalog items belonging to a specific user.
    This endpoint will be consumed by the mobile/frontend application.
    """
    try:
        catalogs = db.query(CatalogDB).filter(CatalogDB.user_id == user_id).all()
        
        if not catalogs:
            raise HTTPException(status_code=404, detail="No catalogs found for this user.")
            
        return {
            "status": "success",
            "user_id": user_id,
            "total_items": len(catalogs),
            "data": catalogs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database Fetch Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching catalogs")