from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# region Основные клавиатуры


def auth_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=
    [
        [
            KeyboardButton(text='🔑 Авторизация')
        ],
        [
            KeyboardButton(text='🔐 Регистрация')
        ]
    ], resize_keyboard=True)

    return kb


def register_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=
                             [
                                 [
                                     KeyboardButton(text='Номер Telegram', request_contact=True),
                                     KeyboardButton(text='Другой номер')
                                 ],
                                 [
                                     KeyboardButton(text='❌ Отмена')
                                 ]
                             ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return kb

# endregion

# region Клавиатура в личном кабинете

# endregion
