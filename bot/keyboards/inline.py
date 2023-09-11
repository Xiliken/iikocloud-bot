from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


def contacts_inline_kb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=
    [
        [
            InlineKeyboardButton(text='Донерс на Мира', callback_data='doners_mira'),
            InlineKeyboardButton(text='Донерс на Крас.рабе', callback_data='doners_krasrab')
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


def sell_inline_kb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=
                                                     [
                                                         [
                                                             InlineKeyboardButton(text='К покупкам', web_app=WebAppInfo(url='https://doners-club.ru/?category=shaurma'))
                                                         ]
                                                     ])

    return ikb

