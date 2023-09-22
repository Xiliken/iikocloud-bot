from sqlalchemy import select

from bot.database import create_async_engine, get_async_session_maker
from bot.database.models import User
from bot.mics import Config, normalize_phone_number


async def get_last_order_date(**kwargs):
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    if "phone" in kwargs:
        if not isinstance(kwargs["phone"], (str, int)):
            raise ValueError("phone must be a string or integer")

        async with session_maker.begin() as session:
            user = await session.execute(
                select(User.last_order_date).filter(
                    User.phone_number == normalize_phone_number(kwargs["phone"])
                )
            )

            last_order_date = user.scalar_one_or_none()

            if last_order_date is None:
                return None

            return last_order_date.strftime("%Y-%m-%d %H:%M")

    if "user_id" in kwargs:
        if not isinstance(kwargs["user_id"], (str, int)):
            raise ValueError("user_id must be a string or integer")

        async with session_maker.begin() as session:
            user = await session.execute(
                select(User.last_order_date).filter(User.user_id == kwargs["user_id"])
            )
            last_order_date = user.scalar_one_or_none()

            if last_order_date is None:
                return None

            return last_order_date.strftime("%Y-%m-%d %H:%M")

    raise ValueError("phone or user_id must be provided")
