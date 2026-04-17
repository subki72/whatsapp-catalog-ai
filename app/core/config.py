from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    GROQ_API_KEY: str
    

    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "wa-catalog-bot"
    
    # SQLite for MVP; switch to PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./catalog_db.sqlite"


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()