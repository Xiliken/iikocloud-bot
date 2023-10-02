from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def admin_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("📊 Статистика")),
                KeyboardButton(text=_("🙍 Пользователи")),
            ],
            [
                KeyboardButton(text=_("📦 Резервная копия БД")),
                KeyboardButton(text=_("📣 Рассылка")),
            ],
            [KeyboardButton(text=_("⬅️ В главное меню"))],
        ],
        resize_keyboard=True,
    )

    return kb
