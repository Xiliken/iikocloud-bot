"""Методы для работы с БД"""

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from bot.database.models.Base import Base
from bot.mics.helpers.Config import Config


async def create_async_engine(url: URL | str) -> AsyncEngine:
    """
    Создания соединения с БД
    :param url: url для подключения к БД
    :return: AsyncEngine
    """
    return _create_async_engine(url=url, echo=Config.get("DEBUG", "bool"))


async def init_models(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_async_session_maker(engine: AsyncEngine):
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, future=True
    )
