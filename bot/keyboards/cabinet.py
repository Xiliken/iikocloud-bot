from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cabinet_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=
        [
            [
                KeyboardButton(text='🎁 Бонусы'),
                KeyboardButton(text='💬 Чат')
            ],
            [
                KeyboardButton(text='👨🏻‍🍳 Меню'),
                KeyboardButton(text='🔥 Акции'),
            ],
            [
                KeyboardButton(text='👤 Контакты')
            ]
        ],
        resize_keyboard=True
    )

    return kb
