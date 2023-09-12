from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.User import User


async def user_exists(id: str | int):
    pass
