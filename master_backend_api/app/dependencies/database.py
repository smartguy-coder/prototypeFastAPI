from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from applications.base_model_and_mixins.base_models import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_async_session_instance() -> AsyncSession:
    session_gen = get_async_session()
    try:
        session = await anext(session_gen)
        return session
    finally:
        await session_gen.aclose()
