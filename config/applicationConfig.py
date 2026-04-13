from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Application configuration loaded from environment variables with validation."""

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str | None = Field(
        default=None,
        description="Full SQLAlchemy URL; if set, overrides discrete DB_* fields.",
    )

    db_host: str = Field(default="localhost", min_length=1, max_length=253)
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str = Field(default="gaserp", min_length=1, max_length=63)
    db_user: str = Field(default="gaserp", min_length=1, max_length=63)
    db_password: SecretStr = Field(default="gaserp")

    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0, le=100)
    db_pool_timeout: int = Field(default=30, ge=1, le=300)
    db_pool_recycle: int = Field(default=1800, ge=0, le=86400)
