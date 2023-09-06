from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def contacts_inline_kb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=
    [
        [
            InlineKeyboardButton(text='Донерс на Мира'),
            InlineKeyboardButton(text='Донерс на Крас.рабе')
        ]
    ])

    return ikb


def chat_inline_kb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=
    [
        [
            InlineKeyboardButton(text='Позвать человека', url='https://t.me/done_help')
        ]
    ])

    return ikb

