from contextlib import asynccontextmanager
from datetime import timedelta

import redis.asyncio as redis

from settings import settings


class RedisService:
    def __init__(self):
        self.redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        self.db = 0
        self.redis = redis.from_url(self.redis_url, db=self.db, decode_responses=True)

    @asynccontextmanager
    async def get_redis(self):
        """
        Контекстний менеджер для роботи з Redis.

        Використовується для автоматичного закриття підключення після виконання операцій.

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            await redis.hset('users:1234', 'name', 'Alex')
        ```
        """
        try:
            yield self.redis
        finally:
            await self.redis.close()

    async def hset(
        self, key: str, field: str, value: str, ttl: int = 60 * 60 * 24 * 90
    ):
        """
        Встановлює значення для певного поля в Redis хеші.

        Args:
            key (str): Ключ хешу.
            field (str): Поле хешу.
            value (str): Значення для поля.
            ttl (int, optional): Час життя ключа в секундах (за замовчуванням 90 днів).

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            await redis_service.hset('users:1234', 'name', 'Alex')
        ```
        """
        async with self.get_redis() as redis:
            await redis.hset(key, field, value)
            await redis.expire(key, ttl)

    async def hget(self, key: str, field: str):
        """
        Отримує значення для певного поля в Redis хеші.

        Args:
            key (str): Ключ хешу.
            field (str): Поле хешу.

        Returns:
            str: Значення поля хешу.

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            value = await redis_service.hget('users:1234', 'name')
        ```
        """
        async with self.get_redis() as redis:
            return await redis.hget(key, field)

    async def hgetall(self, key: str):
        """
        Отримує всі поля та значення хешу.

        Args:
            key (str): Ключ хешу.

        Returns:
            dict: Всі поля та значення хешу.

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            data = await redis_service.hgetall('users:1234')
        ```
        """
        async with self.get_redis() as redis:
            return await redis.hgetall(key)

    async def set_cache(self, key: str, value: str, ttl: int = 60):
        """
        Встановлює кешоване значення в Redis з вказаним часом життя (TTL).

        Args:
            key (str): Ключ кешу.
            value (str): Значення для збереження.
            ttl (int): Час життя кешу в секундах (за замовчуванням 60).

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            await redis_service.set_cache('my_key', 'some_value', ttl=120)
        ```
        """
        async with self.get_redis() as redis:
            await redis.setex(key, timedelta(seconds=ttl), value)

    async def get_cache(self, key: str):
        """
        Отримує кешоване значення з Redis.

        Args:
            key (str): Ключ кешу.

        Returns:
            str: Кешоване значення.

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            value = await redis_service.get_cache('my_key')
        ```
        """
        async with self.get_redis() as redis:
            return await redis.get(key)

    async def delete_cache(self, key: str):
        """
        Видаляє кеш з Redis за вказаним ключем.

        Args:
            key (str): Ключ кешу.

        Приклад використання:
        ```python
        async with redis_service.get_redis() as redis:
            await redis_service.delete_cache('my_key')
        ```
        """
        async with self.get_redis() as redis:
            await redis.delete(key)


redis_service = RedisService()
