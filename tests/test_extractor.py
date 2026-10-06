"""Tests for AI extractor primary chain, fallback chain, and failure modes."""

from unittest.mock import AsyncMock

import pytest
from langchain_core.exceptions import OutputParserException

from app.models.pydantic_schemas import CatalogItem
from app.services.ai_extractor import (
    ERROR_TYPE_PARSE,
    ERROR_TYPE_RATE_LIMIT,
    ERROR_TYPE_SERVICE_UNAVAILABLE,
    AIExtractor,
)


@pytest.mark.asyncio
async def test_ai_extractor_success():
    extractor = AIExtractor()
    mock_item = CatalogItem(
        product_name="Warung Bakso Enak",
        location="Malang",
        menus=["Bakso Mercon", "Es Jeruk"],
        unique_selling_point="Bakso jumbo murah",
    )
    extractor.primary_chain = AsyncMock()
    extractor.primary_chain.ainvoke.return_value = mock_item

    msg = "Tolong buatkan katalog Warung Bakso Enak di Malang"
    result = await extractor.extract_catalog_data(msg)
    assert result["product_name"] == "Warung Bakso Enak"
    assert result["location"] == "Malang"
    assert result["menus"] == ["Bakso Mercon", "Es Jeruk"]


@pytest.mark.asyncio
async def test_ai_extractor_fallback_on_primary_failure(mocker):
    mocker.patch("asyncio.sleep", AsyncMock())
    extractor = AIExtractor()
    extractor.primary_chain = AsyncMock()
    extractor.primary_chain.ainvoke.side_effect = Exception("Groq 429 Rate Limit Exceeded")

    fallback_item = CatalogItem(
        product_name="Warung Fallback",
        location="Jakarta",
        menus=["Mie Ayam"],
        unique_selling_point="Murah meriah",
    )
    extractor.fallback_chain = AsyncMock()
    extractor.fallback_chain.ainvoke.return_value = fallback_item

    result = await extractor.extract_catalog_data("Tolong buatkan katalog Warung Fallback")
    assert result["product_name"] == "Warung Fallback"
    assert extractor.primary_chain.ainvoke.called
    assert extractor.fallback_chain.ainvoke.called


@pytest.mark.asyncio
async def test_ai_extractor_complete_failure(mocker):
    mocker.patch("asyncio.sleep", AsyncMock())
    extractor = AIExtractor()
    extractor.primary_chain = AsyncMock()
    extractor.primary_chain.ainvoke.side_effect = Exception("Primary network error")
    extractor.fallback_chain = AsyncMock()
    extractor.fallback_chain.ainvoke.side_effect = Exception("General connection failure")

    result = await extractor.extract_catalog_data("Any message")
    assert result["product_name"] == "Error"
    assert result["location"] == "Error"
    assert result["menus"] == []
    assert result["error_type"] == ERROR_TYPE_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_ai_extractor_parse_error(mocker):
    mocker.patch("asyncio.sleep", AsyncMock())
    extractor = AIExtractor()
    extractor.primary_chain = AsyncMock()
    extractor.primary_chain.ainvoke.side_effect = OutputParserException("Could not parse JSON")
    extractor.fallback_chain = AsyncMock()
    extractor.fallback_chain.ainvoke.side_effect = OutputParserException("Could not parse JSON")

    result = await extractor.extract_catalog_data("Unstructured incomprehensible message")
    assert result["product_name"] == "Error"
    assert result["error_type"] == ERROR_TYPE_PARSE
    assert "Failed to parse" in result["unique_selling_point"]


@pytest.mark.asyncio
async def test_ai_extractor_rate_limit_error(mocker):
    mocker.patch("asyncio.sleep", AsyncMock())
    extractor = AIExtractor()
    extractor.primary_chain = AsyncMock()
    extractor.primary_chain.ainvoke.side_effect = Exception("429 Too Many Requests")
    extractor.fallback_chain = AsyncMock()
    extractor.fallback_chain.ainvoke.side_effect = Exception("TPM rate limit exceeded")

    result = await extractor.extract_catalog_data("Any message")
    assert result["product_name"] == "Error"
    assert result["error_type"] == ERROR_TYPE_RATE_LIMIT
