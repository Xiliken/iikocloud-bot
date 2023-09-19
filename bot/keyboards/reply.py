from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# region Основные клавиатуры


def auth_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("🔑 Авторизация"))],
            [KeyboardButton(text=_("🔐 Регистрация"))],
        ],
        resize_keyboard=True,
    )

    return kb


def register_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Номер Telegram"), request_contact=True),
                KeyboardButton(text=_("Другой номер")),
            ],
            [KeyboardButton(text=_("❌ Отмена"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return kb


def cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=_("❌ Отмена"))]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return kb
