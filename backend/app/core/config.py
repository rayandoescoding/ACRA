from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and environment configuration loader.
    """

    APP_NAME: str = "ACRA"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "https://acra-3fjo.vercel.app",
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/acra"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    # JWT
    JWT_SECRET_KEY: str = "change-this-development-jwt-secret-before-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Bootstrap administrator
    AUTH_BOOTSTRAP_ADMIN_EMAIL: str | None = None
    AUTH_BOOTSTRAP_ADMIN_PASSWORD: str | None = None

    # Demo data
    DEMO_SEED_ENABLED: bool = False

    # Load from .env / Railway variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Shared settings instance
settings = Settings()