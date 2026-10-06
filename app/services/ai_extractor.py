"""AI-powered catalog information extraction using LangChain and Groq LLMs."""

import asyncio
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logger import logger
from app.models.pydantic_schemas import CatalogItem

EXTRACTION_ERROR = "Error"
MISSING_VALUE = "Tidak disebutkan"
EMPTY_NAME_VALUES = {MISSING_VALUE.lower(), "not provided", "none", ""}

ERROR_TYPE_PARSE = "parse_error"
ERROR_TYPE_SERVICE_UNAVAILABLE = "service_unavailable"
ERROR_TYPE_RATE_LIMIT = "rate_limit"


def _create_error_result(
    error_type: str = ERROR_TYPE_SERVICE_UNAVAILABLE, reason: str = ""
) -> dict:
    """Constructs a standardized dictionary representing an AI extraction error."""
    return {
        "product_name": EXTRACTION_ERROR,
        "location": EXTRACTION_ERROR,
        "menus": [],
        "unique_selling_point": reason or "Failed to extract data",
        "error_type": error_type,
    }


class AIExtractor:
    """Extracts structured catalog items from unstructured user text messages."""

    def __init__(self) -> None:
        self.parser = PydanticOutputParser(pydantic_object=CatalogItem)

        self.prompt = PromptTemplate(
            template=(
                "You are an expert data extraction AI. Your task is to extract business catalog "
                "information from the user's unstructured text message.\n\n"
                "User Message:\n"
                "'{user_message}'\n\n"
                "Instructions:\n"
                "Extract the product name, location, menu list, and unique selling points.\n"
                "If any information is missing, use 'Tidak disebutkan' for strings and "
                "an empty array [] for lists.\n"
                "Answer in the same language as the user message (predominantly Indonesian).\n\n"
                "{format_instructions}\n"
            ),
            input_variables=["user_message"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

        self.primary_llm = None
        self.fallback_llm = None
        self.primary_chain = None
        self.fallback_chain = None
        self._init_llms()

    def _init_llms(self) -> None:
        """Initializes primary and fallback Groq chat models and their execution chains."""
        try:
            api_key = settings.GROQ_API_KEY or "dummy_key"
            self.primary_llm = ChatGroq(
                groq_api_key=api_key,
                model_name=settings.GROQ_MODEL,
                temperature=0,
                max_retries=2,
            )
            self.fallback_llm = ChatGroq(
                groq_api_key=api_key,
                model_name=settings.GROQ_FALLBACK_MODEL,
                temperature=0,
                max_retries=2,
            )
            self.primary_chain = self.prompt | self.primary_llm | self.parser
            self.fallback_chain = self.prompt | self.fallback_llm | self.parser
        except Exception as exc:
            logger.warning("Could not fully initialize Groq chains: %s", exc)

    async def _invoke_with_retry(
        self,
        chain: Runnable,
        user_message: str,
        max_attempts: int = 2,
        retry_delay: float = 1.0,
    ) -> CatalogItem:
        """Invokes a LangChain runnable chain, retrying with exponential backoff on rate limits."""
        last_error = None
        for attempt in range(1, max_attempts + 1):
            try:
                return await chain.ainvoke({"user_message": user_message})
            except Exception as exc:
                last_error = exc
                err_str = str(exc).lower()
                is_rate_limit = "429" in err_str or "rate limit" in err_str or "tpm" in err_str
                if attempt < max_attempts and is_rate_limit:
                    wait_seconds = (2 ** (attempt - 1)) * retry_delay
                    logger.warning(
                        "Groq rate limit hit (attempt %d/%d). Backing off for %.1fs...",
                        attempt,
                        max_attempts,
                        wait_seconds,
                    )
                    await asyncio.sleep(wait_seconds)
                else:
                    break
        raise last_error

    async def extract_catalog_data(self, user_message: str) -> dict:
        """Extracts structured catalog data from a given user message.

        Attempts the primary model with retry backoff, then falls back to the faster 8B model.
        """
        if not self.primary_chain:
            self._init_llms()

        def _to_dict(item: Any) -> dict:
            """Converts a parsed CatalogItem or dict into a validated dictionary format."""
            if hasattr(item, "model_dump"):
                return item.model_dump()
            elif isinstance(item, dict):
                return item
            return _create_error_result(ERROR_TYPE_PARSE, "Invalid result format")

        last_error = None

        # 1. Try primary model with retries
        try:
            if self.primary_chain:
                result = await self._invoke_with_retry(
                    self.primary_chain, user_message, max_attempts=2
                )
                return _to_dict(result)
        except Exception as primary_exc:
            last_error = primary_exc
            logger.warning(
                "Primary LLM (%s) failed: %s. Attempting fallback to %s...",
                settings.GROQ_MODEL,
                primary_exc,
                settings.GROQ_FALLBACK_MODEL,
            )

            # 2. Try fallback model
            try:
                if self.fallback_chain:
                    result = await self._invoke_with_retry(
                        self.fallback_chain, user_message, max_attempts=2
                    )
                    return _to_dict(result)
            except Exception as fallback_exc:
                last_error = fallback_exc
                logger.error(
                    "Fallback LLM (%s) also failed: %s",
                    settings.GROQ_FALLBACK_MODEL,
                    fallback_exc,
                    exc_info=True,
                )

        if isinstance(last_error, OutputParserException):
            return _create_error_result(
                error_type=ERROR_TYPE_PARSE,
                reason="Failed to parse catalog structure from message",
            )
        err_str = str(last_error).lower() if last_error else ""
        if "429" in err_str or "rate limit" in err_str or "tpm" in err_str:
            return _create_error_result(
                error_type=ERROR_TYPE_RATE_LIMIT,
                reason="AI service rate limit exceeded",
            )
        return _create_error_result(
            error_type=ERROR_TYPE_SERVICE_UNAVAILABLE,
            reason="AI service unavailable",
        )
