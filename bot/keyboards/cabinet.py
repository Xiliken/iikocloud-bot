from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def cabinet_main_kb() -> ReplyKeyboardMarkup:
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=
        [
            [
                KeyboardButton(text='🎁 Бонусы'),
                KeyboardButton(text='💬 Чат')
            ],
            [
                KeyboardButton(text='👨🏻‍🍳 Меню', web_app=WebAppInfo(url='https://doners-club.ru/')),
                KeyboardButton(text='🔥 Акции', web_app=WebAppInfo(url='https://doners-club.ru/promotions')),
            ],
            [
                KeyboardButton(text='👤 Контакты')
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню для работы с ботом'
    )

    return kb
