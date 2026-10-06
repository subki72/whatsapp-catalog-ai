"""Lightweight schema migration helpers for adding missing columns."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.core.logger import logger


def run_migrations(engine: Engine) -> None:
    """Applies non-destructive schema migrations to existing database instances.

    Adds missing timestamp columns to the catalogs table across SQLite and PostgreSQL.
    """
    try:
        with engine.connect() as conn:
            inspector = inspect(conn)
            if "catalogs" in inspector.get_table_names():
                columns = [c["name"] for c in inspector.get_columns("catalogs")]
                is_sqlite = engine.dialect.name == "sqlite"

                if "created_at" not in columns:
                    logger.info("Migrating schema: adding created_at column to catalogs table")
                    if is_sqlite:
                        conn.execute(text("ALTER TABLE catalogs ADD COLUMN created_at TIMESTAMP"))
                        conn.execute(
                            text(
                                "UPDATE catalogs SET created_at = CURRENT_TIMESTAMP "
                                "WHERE created_at IS NULL"
                            )
                        )
                    else:
                        conn.execute(
                            text(
                                "ALTER TABLE catalogs ADD COLUMN created_at "
                                "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
                            )
                        )

                if "updated_at" not in columns:
                    logger.info("Migrating schema: adding updated_at column to catalogs table")
                    if is_sqlite:
                        conn.execute(text("ALTER TABLE catalogs ADD COLUMN updated_at TIMESTAMP"))
                        conn.execute(
                            text(
                                "UPDATE catalogs SET updated_at = CURRENT_TIMESTAMP "
                                "WHERE updated_at IS NULL"
                            )
                        )
                    else:
                        conn.execute(
                            text(
                                "ALTER TABLE catalogs ADD COLUMN updated_at "
                                "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
                            )
                        )

                conn.commit()
    except Exception as exc:
        logger.warning("Schema migration notice: %s", exc)
