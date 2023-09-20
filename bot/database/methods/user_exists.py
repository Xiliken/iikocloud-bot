from typing import Union

from sqlalchemy import select

from bot.database import create_async_engine, get_async_session_maker
from bot.database.models.User import User
from bot.mics.helpers.Config import Config


async def user_exists(id: Union[str, int]):
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as conn:
        user = await conn.scalars(select(User).where(User.user_id == msg.from_user.id))
        user = user.first()
    pass
