from aiogram import Bot
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from aiogram.utils.i18n import gettext as _


async def notify(bot: Bot, chat_id, message, reply_markup=None, parse_mode="HTML"):
    await bot.send_message(
        chat_id=chat_id, text=message, reply_markup=reply_markup, parse_mode=parse_mode
    )
