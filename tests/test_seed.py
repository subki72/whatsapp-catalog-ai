"""Tests for database seed utility and production safeguards."""

import pytest

import app.core.database as core_db
from app.core.config import settings
from app.models.schema import CatalogDB
from seed import seed_food_beverage_catalogs


def test_seed_execution_and_idempotency():
    # First run: should create 12 dummy records
    seed_food_beverage_catalogs()

    db = core_db.SessionLocal()
    try:
        count = db.query(CatalogDB).count()
        assert count == 12

        # Verify a sample record
        sample = db.query(CatalogDB).filter(CatalogDB.user_id == "628000000001").first()
        assert sample is not None
        assert sample.product_name == "Nasi Goreng Gila Gondrong"
    finally:
        db.close()

    # Second run: should update, not duplicate
    seed_food_beverage_catalogs()

    db = core_db.SessionLocal()
    try:
        count_after = db.query(CatalogDB).count()
        assert count_after == 12
    finally:
        db.close()


def test_seed_production_wipe_safeguard(monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setenv("FORCE_RESEED", "true")
    monkeypatch.delenv("CONFIRM_PRODUCTION_WIPE", raising=False)

    with pytest.raises(RuntimeError, match="DANGER: FORCE_RESEED is blocked"):
        seed_food_beverage_catalogs()


def test_seed_windows_docker_path_safeguard(monkeypatch):
    monkeypatch.setattr("os.name", "nt")
    monkeypatch.setattr(settings, "DATABASE_URL", "sqlite:////app/data/catalog.sqlite")

    with pytest.raises(RuntimeError, match="DATABASE_URL still points to the Docker path"):
        seed_food_beverage_catalogs()
