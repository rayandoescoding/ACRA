from typing import List
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
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:8000"]
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/acra"

    # Allow configuration values to be read from a .env file if it exists
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Globally shared settings instance
settings = Settings()

