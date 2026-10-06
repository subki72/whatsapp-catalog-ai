"""Application configuration management via Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    GROQ_API_KEY: str = "mock-groq-api-key"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODEL: str = "llama-3.1-8b-instant"

    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "wa-catalog-bot"

    # Webhook security & WhatsApp gateway
    WEBHOOK_SECRET: str = ""
    FONNTE_TOKEN: str = ""
    FONNTE_API_URL: str = "https://api.fonnte.com/send"
    APP_BASE_URL: str = "http://localhost:8000"

    # Environment & CORS
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "*"

    # Database configuration
    DATABASE_URL: str = "sqlite:///./catalog_db.sqlite"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
