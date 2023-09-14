"""Методы для работы с БД"""

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from bot.mics.helpers.Config import Config


def create_async_engine(url: URL| str) -> AsyncEngine:
    """
    Создания соединения с БД
    :param url: url для подключения к БД
    :return: AsyncEngine
    """
    return _create_async_engine(url=url, echo=Config.get('DEBUG', 'bool', pool_pre_ping=True))