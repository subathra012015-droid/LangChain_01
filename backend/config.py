"""Application configuration loaded from environment variables.

This module provides one validated configuration object for the backend.
Values come from the operating-system environment or the local .env file.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate the project root using this file's position.
# This avoids depending on the directory from which the program is started.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Validate configuration required by the application foundation.

    Attributes:
        app_name: Human-readable application name.
        app_env: Currently selected runtime environment.
        backend_host: Network address on which FastAPI will listen.
        backend_port: TCP port on which FastAPI will listen.
        backend_url: URL the frontend will use to contact FastAPI.
        database_url: SQLAlchemy connection string for SQLite.

    Security:
        Future secrets will be read through this class, but they must never
        be printed, returned by an API endpoint, or committed to Git.
    """

    app_name: str = Field(min_length=1)
    app_env: Literal["development", "testing", "production"]
    backend_host: str = Field(min_length=1)
    backend_port: int = Field(ge=1, le=65535)
    backend_url: AnyHttpUrl
    database_url: str = Field(min_length=1)

    # Operating-system environment variables take priority. The .env file
    # supplies local values when an operating-system value is unavailable.
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Load and cache the validated application configuration.

    Returns:
        A Settings object populated from environment variables or .env.

    Raises:
        pydantic.ValidationError: If a required value is missing or invalid.

    The cache prevents the application from reading and validating the same
    configuration repeatedly during a single process.
    """

    return Settings()
