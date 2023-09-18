from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

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


def contacts_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=
    [
        [
            InlineKeyboardButton(text='Донерс на Мира', url='https://2gis.ru/krasnoyarsk/branches/70000001059365039/firm/70000001070530973/92.879245%2C56.012341?m=92.879243%2C56.01235%2F18'),
        ],
        [
            InlineKeyboardButton(text='Донерс на Крас.рабе',
                                 url='https://2gis.ru/krasnoyarsk/branches/70000001059365039/firm/70000001059365040/92.969173%2C56.01198?m=92.96918%2C56.011972%2F18')
        ]
    ])

    return ikb
