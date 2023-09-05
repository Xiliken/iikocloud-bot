from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def contacts_inline_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=
                               [
                                   [
                                       InlineKeyboardButton(text='Донерс на Мира'),
                                       InlineKeyboardButton(text='Донерс на Крас.рабе')
                                   ]
                               ])