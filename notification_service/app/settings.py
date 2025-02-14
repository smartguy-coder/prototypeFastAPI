from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SnapShop notification service"
    PROJECT_VERSION: str = "0.0.1"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    DEBUG: bool = False

    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_DATABASES: int
    REDIS_HOST: str
    REDIS_CACHE_PREFIX: str = "fastapi-cache"

    RABBITMQ_HOSTNAME: str
    RABBITMQ_CONTAINER_NAME: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_AMQP_PORT: int

    @property
    def RABBITMQ_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@"
            f"{self.RABBITMQ_HOSTNAME}:{self.RABBITMQ_AMQP_PORT}/"
        )


@lru_cache()
def get_settings() -> Settings:
    _settings = Settings()
    return _settings


settings = get_settings()
