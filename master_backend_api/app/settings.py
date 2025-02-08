from functools import lru_cache

from pydantic import AnyHttpUrl, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SnapShop 📸🛍️"
    PROJECT_VERSION: str = "0.0.1"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    DEBUG: bool = False

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    DEFAULT_ADMIN_USER_EMAIL: EmailStr
    DEFAULT_ADMIN_USER_PASSWORD: str
    DEFAULT_ADMIN_USER_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    _settings = Settings()
    return _settings


settings = get_settings()
