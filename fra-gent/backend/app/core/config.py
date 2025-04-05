"""
Configuration settings for the Fra-Gent API server.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Project info
    PROJECT_NAME: str = "Fra-Gent"
    PROJECT_DESCRIPTION: str = "AI Agent Framework"
    VERSION: str = "0.1.0"

    # API settings
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS settings are defined directly in main.py

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fragent"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB') or ''}"

    # LLM settings
    DEFAULT_MODEL: str = "gpt-4"
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()
