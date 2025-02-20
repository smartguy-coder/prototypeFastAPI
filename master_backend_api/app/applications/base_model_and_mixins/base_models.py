import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from settings import settings

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(
    logging.DEBUG if settings.DEBUG else logging.INFO
)

engine = create_async_engine(
    settings.DATABASE_URL,
    # echo=settings.DEBUG,  # alternative for logging
)
sync_engine = create_engine(settings.DATABASE_URL_SYNC)  # for sqladmin

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
