"""Catalog retrieval API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Query as SAQuery, Session

from app.core.database import get_db
from app.core.logger import logger
from app.models.schema import CatalogDB

router = APIRouter()

DEFAULT_PAGINATION_LIMIT = 20
MAX_PAGINATION_LIMIT = 100


def _paginate(query: SAQuery, limit: int, offset: int, extra: dict | None = None) -> dict:
    """Helper to paginate a SQLAlchemy query and return standardized response format."""
    total_items = query.count()
    items = (
        query.order_by(CatalogDB.created_at.desc(), CatalogDB.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    result = {
        "status": "success",
        "total_items": total_items,
        "limit": limit,
        "offset": offset,
        "data": jsonable_encoder(items),
    }
    if extra:
        result.update(extra)
    return result


@router.get("/")
def get_all_catalogs(
    limit: int = Query(
        DEFAULT_PAGINATION_LIMIT,
        ge=1,
        le=MAX_PAGINATION_LIMIT,
        description="Number of catalogs to return",
    ),
    offset: int = Query(0, ge=0, description="Number of catalogs to skip"),
    db: Session = Depends(get_db),
) -> dict:
    """Fetch catalog items with pagination across all users (Homepage).

    Ordered by newest first.
    Runs synchronously so FastAPI offloads to worker threadpool.
    """
    try:
        query = db.query(CatalogDB)
        return _paginate(query, limit, offset)
    except Exception as exc:
        logger.error("Database fetch error in get_all_catalogs: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}/catalogs")
def get_user_catalogs(
    user_id: str,
    limit: int = Query(
        DEFAULT_PAGINATION_LIMIT,
        ge=1,
        le=MAX_PAGINATION_LIMIT,
        description="Number of catalogs to return",
    ),
    offset: int = Query(0, ge=0, description="Number of catalogs to skip"),
    db: Session = Depends(get_db),
) -> dict:
    """Return a paginated list of catalogs owned by one WhatsApp number (used by the web UI).

    Runs synchronously so FastAPI offloads to worker threadpool.
    """
    clean_user_id = user_id.strip().lstrip("+")
    try:
        query = db.query(CatalogDB).filter(CatalogDB.user_id == clean_user_id)
        result = _paginate(query, limit, offset, extra={"user_id": clean_user_id})
        if result["total_items"] == 0:
            raise HTTPException(status_code=404, detail="No catalogs found for this user.")

        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Database fetch error in get_user_catalogs: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
