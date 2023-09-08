import asyncio
import logging

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.fsm.strategy import FSMStrategy

from bot.handlers.user import registration_handlers, other_handlers, cabinet_handlers
from bot.mics.commands import set_commands
from bot.mics.helpers.Config import Config
from bot.mics.iikoapi import get_organizations_ids
from bot.handlers import user, admin


async def __on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)

    # Получаем список организаций
    org_ids = get_organizations_ids()

    Config.set('IIKOCLOUD_ORGANIZATIONS_IDS', org_ids)


async def start_bot() -> None:
    # Дебаг
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] -  %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    # Инициализация бота и Redis
    bot: Bot = Bot(token=Config.get('TELEGRAM_BOT_API_KEY'))
    redis: Redis = Redis(host=Config.get('REDIS_HOST'))
    dp: Dispatcher = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)

    # Регистрация дополнительного функционала перед запуском бота
    dp.startup.register(__on_startup)

    # Регистрация роутов
    dp.include_routers(user.router)
    dp.include_routers(registration_handlers.router)
    dp.include_routers(other_handlers.router)
    dp.include_routers(cabinet_handlers.router)
    # dp.include_routers()

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
