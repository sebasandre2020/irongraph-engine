"""Application Configuration & Environment Settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """IronGraph-Engine application settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8005

    # Database & Cache
    DATABASE_URL: str = "postgresql+asyncpg://irongraph:irongraph_secret@localhost:5435/irongraph_db"
    REDIS_URL: str = "redis://localhost:6381/0"

    # Vector Storage
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6335

    # LLM Providers
    LLM_PRIMARY_PROVIDER: str = "minimax"
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_BASE_URL: str = "https://api.minimax.io/v1"
    MINIMAX_MODEL: str = "MiniMax-M3"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Observability
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"


settings = Settings()
