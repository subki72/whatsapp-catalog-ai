"""Tests for automatic schema migration of timestamp columns."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from app.core.migrations import run_migrations


def test_run_migrations_adds_missing_columns():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(
            text(
                """
            CREATE TABLE catalogs (
                id INTEGER PRIMARY KEY,
                user_id VARCHAR,
                product_name VARCHAR,
                location VARCHAR,
                menus JSON,
                unique_selling_point TEXT
            )
        """
            )
        )
        conn.execute(
            text(
                """
            INSERT INTO catalogs (user_id, product_name, location, unique_selling_point)
            VALUES ('6281111111', 'Toko Lama', 'Surabaya', 'Murah')
        """
            )
        )
        conn.commit()

    # Verify initial schema lacks timestamps
    with engine.connect() as conn:
        inspector = inspect(conn)
        cols_before = [c["name"] for c in inspector.get_columns("catalogs")]
        assert "created_at" not in cols_before
        assert "updated_at" not in cols_before

    # Run migration
    run_migrations(engine)

    # Verify columns added
    with engine.connect() as conn:
        inspector = inspect(conn)
        cols_after = [c["name"] for c in inspector.get_columns("catalogs")]
        assert "created_at" in cols_after
        assert "updated_at" in cols_after

        # Verify existing record received default timestamp
        query = text("SELECT created_at, updated_at FROM catalogs WHERE user_id = '6281111111'")
        result = conn.execute(query).fetchone()
        assert result is not None
        assert result[0] is not None
        assert result[1] is not None

    # Run migration again (idempotent)
    run_migrations(engine)
    engine.dispose()
