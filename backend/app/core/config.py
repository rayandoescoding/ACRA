from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and environment configuration loader.
    """

    PROJECT_NAME: str = "ACRA"
    ENVIRONMENT: str = "local"

    # Allow configuration values to be read from a .env file if it exists
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Globally shared settings instance
settings = Settings()
