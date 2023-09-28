from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from aioredis import Redis

from bot.mics import Config

i18n = I18n(path="bot/locales", default_locale="ru", domain="messages")
i18n_middleware = SimpleI18nMiddleware(i18n=i18n)
bot: Bot = Bot(token=Config.get("TELEGRAM_BOT_API_KEY"), parse_mode="HTML")
redis: Redis = Redis(host=Config.get("REDIS_HOST"), port=Config.get("REDIS_PORT") or 6379)
dp: Dispatcher = Dispatcher(storage=RedisStorage(redis=redis), fsm_strategy=FSMStrategy.CHAT)
