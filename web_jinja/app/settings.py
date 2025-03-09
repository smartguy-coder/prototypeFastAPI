from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SnapShop 📸🛍️"
    PROJECT_VERSION: str = "0.0.1"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    DEBUG: bool = False

    SENTRY_DNS: str

    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_DATABASES: int
    REDIS_HOST: str
    REDIS_CACHE_PREFIX: str = "fastapi-cache"

    UDS_PATH: str = "/app/tmp_uds/master-backend.sock"
    UDS_BASE_URL: str = "http://master-backend-api"


@lru_cache()
def get_settings() -> Settings:
    _settings = Settings()
    return _settings


settings = get_settings()
