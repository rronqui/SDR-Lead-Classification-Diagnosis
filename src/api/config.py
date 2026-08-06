import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = ""

    ZAPI_INSTANCE_ID: str = ""
    ZAPI_INSTANCE_TOKEN: str = ""
    ZAPI_SECURITY_TOKEN: str = ""

    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"

    SERPAPI_API_KEY: str = ""

    HUBSPOT_ACCESS_TOKEN: str = ""
    HUBSPOT_OWNER_ID: str = ""

    APP_ENV: str = ""
    LOG_LEVEL: str = ""
    MAX_PERGUNTAS: int = 6

    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "SDR-Lead-Classification-Diagnosis"


settings = Settings()

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", settings.LANGCHAIN_PROJECT)
