from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# region Основные клавиатуры
def main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=
    [
        [
            KeyboardButton(text='🎁 Мои бонусы')
        ]
    ], resize_keyboard=True)

    return kb


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
                                     KeyboardButton(text='Номер Telegram', request_contact=True)
                                 ],
                                 [
                                     KeyboardButton(text='Другой номер')
                                 ]
                             ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    return kb

# endregion

# region Клавиатура в личном кабинете

# endregion