import logging
from dataclasses import dataclass
from os import getenv

from sqlalchemy.engine import URL

#TODO: ДОРАБОТАТЬ И ЗАТЕМ УБРАТЬ config из bot/mics/helpers/Config

@dataclass
class DatabaseConfig:
    """Класс конфигурации для соединения с БД"""

    name: str | None = getenv('DATABASE_NAME')
    user: str | None = getenv('DATABASE_USER')
    passwd: str | None = getenv('DATABASE_PASSWORD', None)
    port: int = int(getenv('DATABASE_PORT', 5432))
    host: str = getenv('DATABASE_HOST', 'db')