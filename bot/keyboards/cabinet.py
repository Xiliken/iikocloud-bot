from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _

def cabinet_main_kb() -> ReplyKeyboardMarkup:
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=
        [
            [
                KeyboardButton(text=_('Бонусная карта')),
                KeyboardButton(text=_('Чат'))
            ],
            [
                KeyboardButton(text=_('Меню'), web_app=WebAppInfo(url='https://doners-club.ru/')),
                KeyboardButton(text=_('Акции'), web_app=WebAppInfo(url='https://doners-club.ru/promotions')),
                KeyboardButton(text=_('Контакты'))
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder=_('Выберите пункт меню для работы с ботом')
    )

    return kb
