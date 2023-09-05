import asyncio
import logging

from aiogram import Bot, F, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

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
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] -  %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")

    bot = Bot(token=Config.get('TELEGRAM_BOT_API_KEY'))
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)

    dp.startup.register(__on_startup)

    # Регистрация роутов
    dp.include_routers(user.router)
    # dp.include_routers()

    # Запускаем бота и пропускаем все накопленные входящие
    await dp.start_polling(bot)
