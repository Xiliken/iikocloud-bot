from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.RateCallbackData import RateCallbackData, RateServiceCallbackData


def chat_inline_kb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_("Позвать человека"), url="https://t.me/done_help")]]
    )

    return ikb


def sell_inline_kb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("К покупкам"),
                    web_app=WebAppInfo(url="https://doners-club.ru/?category=shaurma"),
                )
            ]
        ]
    )

    return ikb


def contacts_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Донерс на Мира",
                    url="https://2gis.ru/krasnoyarsk/branches/70000001059365039/firm/70000001070530973/92.879245%2C56.012341?m=92.879243%2C56.01235%2F18",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Донерс на Крас.рабе",
                    url="https://2gis.ru/krasnoyarsk/branches/70000001059365039/firm/70000001059365040"
                    "/92.969173%2C56.01198?m=92.96918%2C56.011972%2F18",
                )
            ],
        ]
    )

    return ikb


def website_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Открыть меню", url="https://doners-club.ru/")]]
    )

    return ikb


def promotions_ikb() -> InlineKeyboardMarkup:
    ikb: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Открыть список акций", url="https://doners-club.ru/promotions")]]
    )

    return ikb


def rate_last_order_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😡 1", callback_data=RateCallbackData(food_rating=1).pack()),
                InlineKeyboardButton(text="😟 2", callback_data=RateCallbackData(food_rating=2).pack()),
                InlineKeyboardButton(text="😐 3", callback_data=RateCallbackData(food_rating=3).pack()),
                InlineKeyboardButton(text="😚 4", callback_data=RateCallbackData(food_rating=4).pack()),
                InlineKeyboardButton(text="😍 5", callback_data=RateCallbackData(food_rating=5).pack()),
            ]
        ]
    )

    return ikb


# TODO: Изменить это в будущем. User может нажать по любой старой кнопке и она отработает.
#  Надо подумать, как исправить это
def rate_last_service() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😡 1", callback_data=RateServiceCallbackData(rating=1).pack()),
                InlineKeyboardButton(text="😟 2", callback_data=RateServiceCallbackData(rating=2).pack()),
                InlineKeyboardButton(text="😐 3", callback_data=RateServiceCallbackData(rating=3).pack()),
                InlineKeyboardButton(text="😚 4", callback_data=RateServiceCallbackData(rating=4).pack()),
                InlineKeyboardButton(text="😍 5", callback_data=RateServiceCallbackData(rating=5).pack()),
            ]
        ]
    )

    return ikb


def hr_ikb() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=_("✉️ Написать HR"), url="https://t.me/HR_sferagroup")
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()
