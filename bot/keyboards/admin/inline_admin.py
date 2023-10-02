from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_report_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_("📋 Сформировать отчет"), callback_data="report")]]
    )

    return ikb


def admin_users_ikb() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=_("👥 Список пользователей"), callback_data="users_list")
    keyboard_builder.button(text=_("👮‍♀️ Администраторы"), callback_data="admins_list")
    keyboard_builder.button(text=_("🔎 Поиск пользователя"), callback_data="search_users")
    keyboard_builder.button(text=_("➕ Добавить пользователя"), callback_data="add_user")
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()


def get_confirm_button_ikb() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=_("Добавить кнопку"), callback_data="add_button")
    keyboard_builder.button(text=_("Продолжить без кнопки"), callback_data="no_button")
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()
