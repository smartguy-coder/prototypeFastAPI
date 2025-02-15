from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    SMTP_TOKEN: str
    SMTP_USER: str
    SMTP_SERVER: str

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
