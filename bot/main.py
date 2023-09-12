import asyncio
import logging

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.database.base import Base
from bot.handlers.user import registration_handlers, other_handlers, cabinet_handlers, login_handlers
from bot.mics.commands import set_commands
from bot.mics.helpers.Config import Config
from bot.mics.iikoapi import get_organizations_ids
from bot.handlers import user, admin
from bot.middlewares.database import DbSessionMiddleware


async def __on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)

    # Получаем список организаций
    org_ids = get_organizations_ids()

    Config.set('IIKOCLOUD_ORGANIZATIONS_IDS', org_ids)


async def start_bot() -> None:

    # Инициализация базы данных
    engine = create_async_engine(url=Config.get('DATABASE_URL'), echo=Config.get('DATABASE_DEBUG', 'bool'))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)



    # Дебаг
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] -  %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    #region Инициализация бота и Redis
    bot: Bot = Bot(token=Config.get('TELEGRAM_BOT_API_KEY'), parse_mode='HTML')
    redis: Redis = Redis(host=Config.get('REDIS_HOST'))
    dp: Dispatcher = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)
    #endregion

    #region Регистрация MiddleWares
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    #endregion


    #region Регистрация дополнительного функционала перед запуском бота
    dp.startup.register(__on_startup)
    #endregion

    #region Регистрация роутов
    dp.include_routers(other_handlers.router)
    dp.include_routers(user.router)
    dp.include_routers(registration_handlers.router)
    dp.include_routers(login_handlers.router)
    dp.include_routers(cabinet_handlers.router)
    # dp.include_routers()
    #endregion

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
