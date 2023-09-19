from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select

from bot.database import create_async_engine, get_async_session_maker
from bot.database.models import User
from bot.mics import Config


class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

    async def is_admin(self, msg: Message):
        engine = await create_async_engine(url=Config.get("DATABASE_URL"))
        session_maker = get_async_session_maker(engine)

        async with session_maker.begin() as conn:
            user = await conn.scalars(
                select(User).where(User.user_id == msg.from_user.id)
            )
            user = user.first()

            return bool(user.is_admin)
