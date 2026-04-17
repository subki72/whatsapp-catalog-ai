from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 'check_same_thread=False' is required for SQLite with FastAPI's async workers
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    """
    Creates a new database session for a request and closes it once the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()