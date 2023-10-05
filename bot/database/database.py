"""Методы для работы с БД"""
from typing import Union

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from bot.database.models.Base import Base
from bot.mics.helpers.Config import Config


async def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
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
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)


async def check_table_exist(table_name: str, session: AsyncSession) -> bool:
    """
    Проверка существования таблицы в БД
    :param table_name: название таблицы
    :param session: сессия
    :return: bool
    """
    result = await session.execute(
        f"SELECT EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table_name}');"
    )
    return bool(result)
