from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_models import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
