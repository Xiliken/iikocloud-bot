from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cabinet_main_kb() -> ReplyKeyboardMarkup:
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("Бонусная карта")), KeyboardButton(text=_("Чат"))],
            [
                KeyboardButton(text=_("Меню")),
                KeyboardButton(text=_("Акции")),
                KeyboardButton(text=_("Контакты")),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню для работы с ботом"),
    )

    return kb
