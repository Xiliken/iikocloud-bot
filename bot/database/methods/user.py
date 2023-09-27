from typing import List

from sqlalchemy import func, select

from bot.database import create_async_engine, get_async_session_maker
from bot.database.models.User import User
from bot.mics.helpers.Config import Config


# Получить список администраторов
async def get_admins() -> List[User]:
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as session:
        users = await session.execute(select(User).filter(User.is_admin))
        users = users.fetchall()
        await session.commit()

    return list(users)


async def get_all_users(include_blocked: bool = False) -> List[User]:
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    users_list = []

    async with session_maker.begin() as session:
        if include_blocked:
            users = await session.execute(select(User))
            users = users.fetchall()
            users_list = list(users)
            await session.commit()
        else:
            users = await session.execute(select(User).filter(User.is_blocked == False))
            users = users.fetchall()
            users_list = list(users)
            await session.commit()

        return users_list


async def get_users_count():
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as session:
        count = await session.scalar(select(func.count("*")).select_from(User))
        await session.commit()

    return count
