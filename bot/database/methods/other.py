from sqlalchemy import text

from bot.database import create_async_engine, get_async_session_maker
from bot.mics import Config


async def check_table_exist(table_name: str) -> bool:
    """
    Проверка существования таблицы в БД
    :param table_name: название таблицы
    :param session: сессия
    :return: bool
    """

    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as session:
        result = await session.execute(
            text(f"SELECT EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table_name}');")
        )
        return bool(result.scalar())


async def delete_table(table_name):
    """
    Удалить таблицу из БД
    :param table_name:
    :return:
    """
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as session:
        await session.execute(text(f"DROP TABLE {table_name}"))
