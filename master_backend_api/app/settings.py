from functools import lru_cache

from pydantic import AnyHttpUrl, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SnapShop 📸🛍️"
    PROJECT_VERSION: str = "0.0.1"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    DEBUG: bool = False

    JWT_SECRET: str
    JWT_ALGORITHM: str
    REFRESH_TOKEN_TIME_MINUTES: int = 60 * 24  # one day
    ACCESS_TOKEN_TIME_MINUTES: int = 5

    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_DATABASES: int
    REDIS_HOST: str
    REDIS_CACHE_PREFIX: str = "fastapi-cache"

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_DEFAULT_BUCKET_NAME: str
    S3_PORT: int
    S3_ENDPOINT: str

    DEFAULT_ADMIN_USER_EMAIL: EmailStr
    DEFAULT_ADMIN_USER_PASSWORD: str
    DEFAULT_ADMIN_USER_NAME: str

    ADMIN_SECRET_KEY: str

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    RABBITMQ_HOSTNAME: str
    RABBITMQ_CONTAINER_NAME: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_AMQP_PORT: int

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def RABBITMQ_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@"
            f"{self.RABBITMQ_HOSTNAME}:{self.RABBITMQ_AMQP_PORT}/"
        )

    @property
    def S3_URL(self) -> str:
        return f"{self.S3_ENDPOINT}:{self.S3_PORT}"


@lru_cache()
def get_settings() -> Settings:
    _settings = Settings()
    return _settings


settings = get_settings()
