from bot.database import create_async_engine, get_async_session_maker
from bot.mics import Config


async def backup(send_notifications: bool = False):
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as session:
        pass
