from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def cabinet_main_kb() -> ReplyKeyboardMarkup:
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("Бонусная карта")), KeyboardButton(text=_("Чат"))],
            [
                KeyboardButton(text=_("Меню")),
                KeyboardButton(text=_("Акции")),
                KeyboardButton(text=_("Контакты")),
            ],
            [
                KeyboardButton(text=_("Пароль от WiFi")),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=_("Выберите пункт меню для работы с ботом"),
    )

    return kb
