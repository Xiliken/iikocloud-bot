from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def admin_report_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_("📋 Сформировать отчет"), callback_data="report")]]
    )

    return ikb


def admin_users_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("👥 Список пользователей"), callback_data="users_list"),
            ],
            [
                InlineKeyboardButton(text=_("👮‍♀️ Администраторы"), callback_data="admins_list"),
            ],
            [
                InlineKeyboardButton(text=_("🔎 Поиск пользователя"), callback_data="search_users"),
            ],
            [
                InlineKeyboardButton(text=_("➕ Добавить пользователя"), callback_data="add_user"),
            ],
        ]
    )
    return ikb
