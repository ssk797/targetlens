from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or ``.env``.

    The defaults are intentionally local-development-only values. Production
    deployments must provide their own credentials and endpoints through the
    environment; no secret or provider key is stored in source control.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "TargetLens API"
    environment: str = Field(default="development", validation_alias="TARGETLENS_ENV")
    api_mode: str = Field(default="mock", validation_alias="TARGETLENS_API_MODE")
    database_url: str = Field(
        default="postgresql+asyncpg://targetlens:targetlens_dev@localhost:5432/targetlens",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    s3_endpoint: str = Field(default="http://localhost:9000", validation_alias="S3_ENDPOINT")
    s3_access_key: str = Field(default="targetlens", validation_alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="targetlens_dev", validation_alias="S3_SECRET_KEY")
    s3_bucket: str = Field(default="targetlens-artifacts", validation_alias="S3_BUCKET")
    web_origin: str = Field(default="http://localhost:3000", validation_alias="WEB_ORIGIN")
    cors_origins: str = Field(default="http://localhost:3000", validation_alias="CORS_ORIGINS")
    data_cutoff: str | None = Field(default=None, validation_alias="DATA_CUTOFF")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
