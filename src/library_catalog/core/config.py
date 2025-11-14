from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Control Book API"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False

    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # External Services
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0
    openlibrary_cache_ttl: int = 3600  # seconds

    # API
    api_v1_prefix: str = "/api/v1"
    docs_url: str | None = "/docs"

    # Security
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # Logging
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql"):
            raise ValueError("Only PostgreSQL databases are supported")
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION


settings = Settings()
