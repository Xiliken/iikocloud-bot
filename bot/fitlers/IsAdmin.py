from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select

from bot.database import create_async_engine, get_async_session_maker
from bot.database.models import User
from bot.mics import Config


async def is_admin(msg: Message):
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as conn:
        users = await conn.execute(select(User).filter(User.is_admin))

        if not bool(users.fetchall()):
            return False

        for user in users:
            print("Пользователя, которого получили", user)
            if user.user_id != msg.from_user.id:
                return False
        return True


class IsAdmin(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return await is_admin(message)
