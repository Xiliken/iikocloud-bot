from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from loguru import logger

from .DbSessionMiddleware import DbSessionMiddleware

__all__ = ["DbSessionMiddleware"]

from .ThrottlingMiddleware import ThrottlingMiddleware

logger.info("Middlewares are successfully configured")

i18n = I18n(path="bot/locales", default_locale="ru", domain="messages")
i18n_middleware = SimpleI18nMiddleware(i18n=i18n)


def register_all_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(ThrottlingMiddleware())
    dp.update.middleware(i18n_middleware)
