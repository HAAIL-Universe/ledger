"""
Application configuration using pydantic-settings for environment variable management.

Loads configuration from environment variables and .env files, providing
type-validated settings for all application components: database, auth,
external APIs, file uploads, and general application settings.
"""

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings loaded from environment variables.

    All settings are validated at startup. Required fields without defaults
    will cause an immediate error if not provided, preventing misconfigured
    deployments.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    database_url: str = "postgresql+asyncpg://localhost:5432/ledger"

    # -------------------------------------------------------------------------
    # Authentication (JWT)
    # -------------------------------------------------------------------------
    jwt_secret: str = "CHANGE-ME-in-production-use-a-long-random-string"
    jwt_refresh_secret: str = "CHANGE-ME-refresh-secret-must-differ-from-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # -------------------------------------------------------------------------
    # Google Cloud Vision (OCR)
    # -------------------------------------------------------------------------
    google_cloud_vision_credentials: str = ""

    # -------------------------------------------------------------------------
    # OpenAI (NLP)
    # -------------------------------------------------------------------------
    openai_api_key: str = ""

    # -------------------------------------------------------------------------
    # CORS / URLs
    # -------------------------------------------------------------------------
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # -------------------------------------------------------------------------
    # File Upload
    # -------------------------------------------------------------------------
    max_upload_size_mb: int = 10
    allowed_image_types: str = "image/jpeg,image/png,image/webp"

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    environment: str = "production"
    log_level: str = "INFO"

    # -------------------------------------------------------------------------
    # Computed / Derived Properties
    # -------------------------------------------------------------------------

    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum upload size converted to bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def allowed_image_types_list(self) -> List[str]:
        """Allowed image MIME types as a list."""
        return [t.strip() for t in self.allowed_image_types.split(",") if t.strip()]

    @property
    def is_dev(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "dev"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is a valid Python logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid_levels:
            raise ValueError(
                f"Invalid log level '{v}'. Must be one of: {', '.join(sorted(valid_levels))}"
            )
        return upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is a recognized value."""
        valid_envs = {"dev", "staging", "production"}
        lower = v.lower()
        if lower not in valid_envs:
            raise ValueError(
                f"Invalid environment '{v}'. Must be one of: {', '.join(sorted(valid_envs))}"
            )
        return lower

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """Ensure JWT algorithm is supported."""
        supported = {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"}
        if v not in supported:
            raise ValueError(
                f"Unsupported JWT algorithm '{v}'. Must be one of: {', '.join(sorted(supported))}"
            )
        return v

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_access_token_expire(cls, v: int) -> int:
        """Ensure access token expiry is positive."""
        if v <= 0:
            raise ValueError("Access token expiry must be a positive number of minutes.")
        return v

    @field_validator("refresh_token_expire_days")
    @classmethod
    def validate_refresh_token_expire(cls, v: int) -> int:
        """Ensure refresh token expiry is positive."""
        if v <= 0:
            raise ValueError("Refresh token expiry must be a positive number of days.")
        return v

    @field_validator("max_upload_size_mb")
    @classmethod
    def validate_max_upload_size(cls, v: int) -> int:
        """Ensure max upload size is reasonable."""
        if v <= 0:
            raise ValueError("Max upload size must be a positive number of MB.")
        if v > 100:
            raise ValueError("Max upload size cannot exceed 100 MB.")
        return v


def get_settings() -> Settings:
    """
    Factory function to create a Settings instance.

    This function can be used as a FastAPI dependency to inject
    configuration throughout the application.

    Returns:
        Settings: Validated application settings.
    """
    return Settings()


# Module-level singleton for convenience imports.
# Usage: `from app.config import settings`
settings: Settings = get_settings()
