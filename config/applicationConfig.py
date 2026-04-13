from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Application configuration loaded from environment variables with validation."""

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    database_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
        description="Full SQLAlchemy URL; if set, overrides discrete DB_* fields.",
    )

    db_host: str = Field(
        default="localhost",
        min_length=1,
        max_length=253,
        validation_alias=AliasChoices("DB_HOST", "db_host"),
    )
    db_port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        validation_alias=AliasChoices("DB_PORT", "db_port"),
    )
    db_name: str = Field(
        default="gaserp",
        min_length=1,
        max_length=63,
        validation_alias=AliasChoices("DB_NAME", "db_name"),
    )
    db_user: str = Field(
        default="gaserp",
        min_length=1,
        max_length=63,
        validation_alias=AliasChoices("DB_USER", "db_user"),
    )
    db_password: SecretStr = Field(
        default="gaserp",
        validation_alias=AliasChoices("DB_PASSWORD", "db_password"),
    )

    db_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        validation_alias=AliasChoices("DB_POOL_SIZE", "db_pool_size"),
    )
    db_max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        validation_alias=AliasChoices("DB_MAX_OVERFLOW", "db_max_overflow"),
    )
    db_pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        validation_alias=AliasChoices("DB_POOL_TIMEOUT", "db_pool_timeout"),
    )
    db_pool_recycle: int = Field(
        default=1800,
        ge=0,
        le=86400,
        validation_alias=AliasChoices("DB_POOL_RECYCLE", "db_pool_recycle"),
    )

    jwt_secret: SecretStr = Field(
        default=SecretStr("change-me-in-production"),
        validation_alias=AliasChoices("JWT_SECRET", "jwt_secret"),
        description="HS256 signing secret for access tokens.",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        min_length=3,
        max_length=16,
        validation_alias=AliasChoices("JWT_ALGORITHM", "jwt_algorithm"),
    )
    jwt_access_expire_seconds: int = Field(
        default=86400,
        ge=60,
        le=60 * 60 * 24 * 30,
        validation_alias=AliasChoices(
            "JWT_ACCESS_EXPIRE_SECONDS",
            "jwt_access_expire_seconds",
        ),
        description="Access token lifetime in seconds (default 1 day, max 30 days).",
    )
    jwt_refresh_expire_seconds: int = Field(
        default=60 * 60 * 24 * 7,
        ge=300,
        le=60 * 60 * 24 * 90,
        validation_alias=AliasChoices(
            "JWT_REFRESH_EXPIRE_SECONDS",
            "jwt_refresh_expire_seconds",
        ),
        description="Stored refresh token lifetime in seconds (default 7 days, max 90 days).",
    )
