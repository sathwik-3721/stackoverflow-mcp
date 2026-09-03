"""Configuration settings for stackoverflow-mcp."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    STACKEXCHANGE_KEY: str | None = Field(
        default=None,
        description="Optional Stack Exchange API key for 10k daily quota.",
    )
    STACKOVERFLOW_MAX_RESULTS: int = Field(
        default=10,
        ge=1,
        le=10,
        description="Max results per search query (capped at 10).",
    )
    STACKOVERFLOW_API_TIMEOUT_SECONDS: int = Field(
        default=15,
        ge=1,
        description="HTTP request timeout in seconds.",
    )
    STACKOVERFLOW_API_MAX_RETRIES: int = Field(
        default=3,
        ge=0,
        description="Max retry attempts for transient API failures.",
    )
    STACKOVERFLOW_LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR).",
    )


settings = Settings()
