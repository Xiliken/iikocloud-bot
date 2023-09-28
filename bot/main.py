import datetime
import pathlib

import aiocron
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from loguru import logger

import utils
from bot.database import create_async_engine, get_async_session_maker, init_models
from bot.handlers import user
from bot.handlers.admin import base_admin_handlers
from bot.handlers.user import (
    cabinet_handlers,
    login_handlers,
    other_handlers,
    registration_handlers,
)
from bot.mics.commands import set_commands
from bot.mics.helpers.Config import Config
from bot.mics.iikoapi import get_organizations_ids
from bot.middlewares.DbSessionMiddleware import DbSessionMiddleware
from bot.middlewares.ThrottlingMiddleware import ThrottlingMiddleware
from config import settings
from schedulers.sc_check_order import check_last_orders

# Данные пользователя
user_dict: dict[int, dict[str, str | int | bool]] = {}


async def __on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)

    # Получаем список организаций
    org_ids = get_organizations_ids()

    settings.iiko.organizations_ids = org_ids

    Config.set("IIKOCLOUD_ORGANIZATIONS_IDS", org_ids)


async def __on_shutdown(bot: Bot) -> None:
    pass


async def start_bot() -> None:
    # region Инициализация БД
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    await init_models(engine)
    session_maker = get_async_session_maker(engine)

    # endregion

    # region Дебаг
    if Config.get("DEBUG", "bool"):
        log_type = str(Config.get("LOG_TYPE")).lower()

        if log_type == "console":
            utils.logger.setup_logger("DEBUG", ignored=["sqlalchemy", "aiogram"])
        elif log_type == "file":
            log_file = pathlib.Path(
                pathlib.Path().cwd(),
                "logs",
                f'bot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
            )
            utils.logger.setup_logger_file(log_file=log_file, level="DEBUG")
    # endregion

    # region Инициализация бота и Redis
    bot: Bot = Bot(token=Config.get("TELEGRAM_BOT_API_KEY"), parse_mode="HTML")
    redis: Redis = Redis(host=Config.get("REDIS_HOST"), port=Config.get("REDIS_PORT") or 6379)
    dp: Dispatcher = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)

    # region Локализация
    i18n = I18n(path="bot/locales", default_locale="ru", domain="messages")
    i18n_middleware = SimpleI18nMiddleware(i18n=i18n)
    # endregion

    # endregion

    # region Регистрация MiddleWares
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.update.middleware(i18n_middleware)
    dp.message.middleware(ThrottlingMiddleware())
    # endregion

    # region Регистрация дополнительного функционала перед запуском бота
    dp.startup.register(__on_startup)
    dp.shutdown.register(__on_shutdown)
    # endregion

    # region Регистрация роутов
    dp.include_routers(other_handlers.router)
    dp.include_routers(base_admin_handlers.router)
    dp.include_routers(user.router)
    dp.include_routers(registration_handlers.router)
    dp.include_routers(login_handlers.router)
    dp.include_routers(cabinet_handlers.router)
    # dp.include_routers()
    # endregion

    # Запускаем бота и пропускаем все накопленные входящие
    try:
        # region Запуск задач Cron
        aiocron.crontab("* * * * *", func=check_last_orders, args=(), start=True)
        # endregion

        logger.success("~~~~ Bot polling is starting... ~~~~")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await dp.storage.close()
        logger.warning("~~~~ Bot polling is stopped ~~~~")
