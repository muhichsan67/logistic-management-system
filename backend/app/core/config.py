from functools import lru_cache
from typing_extensions import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Semua konfigurasi dibaca dari environment / .env (tidak ada hardcode)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "ALUR Logistik API"
    APP_VERSION: str = "1.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database (wajib driver async: postgresql+asyncpg://)
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # JWT
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 jam sesuai BACKEND_RULES 3.1
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    CORS_ORIGINS: list[str] = []
    BUSINESS_TIMEZONE: str = "Asia/Jakarta"

    # Upload bukti pengiriman
    UPLOAD_DIR: str = "uploads"
    UPLOAD_URL_PREFIX: str = "/static"
    MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024

    # Rate limit login/register
    AUTH_RATE_LIMIT: int = 10
    AUTH_RATE_WINDOW_SECONDS: int = 60

    SCHEDULER_ENABLED: bool = True

    STORAGE_BACKEND: Literal["local", "s3"] = "s3"
    AWS_ENDPOINT_URL_S3: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "auto"
    S3_BUCKET: str = ""
    PRESIGN_EXPIRES_SECONDS: int = 300

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
