
import datetime
import pathlib

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

import utils
from bot.database import create_async_engine, init_models, get_async_session_maker
from bot.handlers import user
from bot.handlers.user import registration_handlers, other_handlers, cabinet_handlers, login_handlers
from bot.mics.changelog import check_changelog
from bot.mics.commands import set_commands
from bot.mics.helpers.Config import Config
from bot.mics.iikoapi import get_organizations_ids
from bot.middlewares.DbSessionMiddleware import DbSessionMiddleware
from config import settings


async def __on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)

    # Получаем список организаций
    org_ids = get_organizations_ids()

    settings.iiko.organizations_ids = org_ids

    Config.set('IIKOCLOUD_ORGANIZATIONS_IDS', org_ids)


async def start_bot() -> None:
    # БД
    engine = await create_async_engine(url=Config.get('DATABASE_URL'))
    await init_models(engine)
    session_maker = get_async_session_maker(engine)

    # Дебаг
    if Config.get('DEBUG', 'bool'):
        match str(Config.get('LOG_TYPE')).lower() or 'console':
            case 'console':
                utils.logger.setup_loger("DEBUG")
            case 'file':
                utils.logger.setup_logger_file(log_file=pathlib.Path(pathlib.Path().cwd(), 'logs',
                                                             f'bot_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'))

    # region Инициализация бота и Redis
    bot: Bot = Bot(token=Config.get('TELEGRAM_BOT_API_KEY'), parse_mode='HTML')
    redis: Redis = Redis(host=Config.get('REDIS_HOST'))
    dp: Dispatcher = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)
    # endregion



    # region Регистрация MiddleWares
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    # endregion

    # region Регистрация дополнительного функционала перед запуском бота
    dp.startup.register(__on_startup)
    # endregion

    # region Регистрация роутов
    dp.include_routers(other_handlers.router)
    dp.include_routers(user.router)
    dp.include_routers(registration_handlers.router)
    dp.include_routers(login_handlers.router)
    dp.include_routers(cabinet_handlers.router)
    # dp.include_routers()
    # endregion

    #region Планировщик задач
    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    changelog = await check_changelog(chat_id=5599795627, bot=bot)
    scheduler.add_job(changelog, trigger='interval', seconds=5)
    #endregion



    # Запускаем бота и пропускаем все накопленные входящие
    try:
        scheduler.start()
        logger.warning('Bot polling is starting...')
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.warning('Bot polling is stopped.')
        scheduler.shutdown(wait=False)
