"""Tests for catalog API endpoints, pagination, and user filtering."""

import pytest

import app.core.database as core_db
from app.models.schema import CatalogDB


@pytest.mark.asyncio
async def test_get_all_catalogs_empty(client):
    response = await client.get("/api/v1/catalogs/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_items"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_get_all_catalogs_pagination(client):
    # Insert dummy items into test db
    db = core_db.SessionLocal()
    try:
        for i in range(5):
            item = CatalogDB(
                user_id=f"62800000000{i}",
                product_name=f"Bisnis {i}",
                location=f"Kota {i}",
                menus=[f"Menu {i}"],
                unique_selling_point=f"USP {i}",
            )
            db.add(item)
        db.commit()
    finally:
        db.close()

    # Request with limit=2, offset=0
    res1 = await client.get("/api/v1/catalogs/?limit=2&offset=0")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total_items"] == 5
    assert len(data1["data"]) == 2
    assert data1["limit"] == 2
    assert data1["offset"] == 0

    # Request second page
    res2 = await client.get("/api/v1/catalogs/?limit=2&offset=2")
    assert res2.status_code == 200
    data2 = res2.json()
    assert len(data2["data"]) == 2
    assert data2["offset"] == 2


@pytest.mark.asyncio
async def test_get_user_catalogs_found_and_not_found(client):
    db = core_db.SessionLocal()
    try:
        item = CatalogDB(
            user_id="628123456789",
            product_name="Kopi Kenangan Mantan",
            location="Bandung",
            menus=["Es Kopi", "Roti"],
            unique_selling_point="Enak dan murah",
        )
        db.add(item)
        db.commit()
    finally:
        db.close()

    # User found
    res_found = await client.get("/api/v1/catalogs/users/628123456789/catalogs")
    assert res_found.status_code == 200
    data_found = res_found.json()
    assert data_found["status"] == "success"
    assert data_found["user_id"] == "628123456789"
    assert len(data_found["data"]) == 1
    assert data_found["data"][0]["product_name"] == "Kopi Kenangan Mantan"

    # User found with plus prefix in URL
    res_plus = await client.get("/api/v1/catalogs/users/+628123456789/catalogs")
    assert res_plus.status_code == 200
    assert res_plus.json()["user_id"] == "628123456789"

    # User not found (404)
    res_not_found = await client.get("/api/v1/catalogs/users/9999999999/catalogs")
    assert res_not_found.status_code == 404
    assert res_not_found.json()["detail"] == "No catalogs found for this user."


@pytest.mark.asyncio
async def test_browser_user_catalog_route_and_security_headers(client):
    response = await client.get("/users/628123456789/catalogs")
    assert response.status_code == 200
    # Verify Content-Security-Policy header
    assert "Content-Security-Policy" in response.headers
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
