from typing import Optional

from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, session
from sqlalchemy.orm import Session

from bot.database import create_async_engine, get_async_session_maker
from bot.database.models.User import User
from bot.mics.helpers.Config import Config


class IsAuth(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return await self.check_user(message)

    async def check_user(self, msg: Message):
        engine = await create_async_engine(url=Config.get('DATABASE_URL'))
        session_maker = get_async_session_maker(engine)

        async with session_maker.begin() as conn:
            user = await conn.scalars(select(User).where(User.user_id == msg.from_user.id))
            user = user.first()

        return bool(user)
