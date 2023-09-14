from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from bot.database.models.User import User


class IsAuth(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return await self.check_user(message)

    async def check_user(self, msg: Message, session: AsyncSession):
        query = await session.execute(select(User).where(User.user_id == msg.from_user.id))

        return bool(query.scalar())



