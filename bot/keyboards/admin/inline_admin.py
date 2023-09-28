from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def admin_report_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_("📋 Сформировать отчет"), callback_data="report")]]
    )

    return ikb
