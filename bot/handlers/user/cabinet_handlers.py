import asyncio
import os

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.User import User
from bot.fitlers.IsAuth import IsAuth
from bot.keyboards import auth_kb
from bot.keyboards.inline import sell_inline_kb
from bot.mics.helpers.Config import Config
from services.iikocloud.enums import TypeRCI
from services.iikocloud.iIkoCloud import IikoCloudAPI
from utils import generate_qr

router: Router = Router()
auth_router: Router = Router()

iiko: IikoCloudAPI = IikoCloudAPI(api_login=Config.get("IIKOCLOUD_LOGIN"))


@router.message(Command(commands=["balance", "money"]), IsAuth())
@router.message(F.text == __("Бонусная карта"), IsAuth())
async def profile_handler(msg: Message, session: AsyncSession):
    bot = msg.bot

    if await session.scalar(exists().where(User.user_id == msg.from_user.id).select()):
        user = await session.scalars(select(User).where(User.user_id == msg.from_user.id))
        user = user.first()

        profile_info = iiko.customer_info(
            organization_id=Config.get("IIKOCLOUD_ORGANIZATIONS_IDS", "list")[0],
            identifier=user.phone_number,
            type=TypeRCI.phone,
        )

        # region Генерация и отправка QR-кода
        generate_qr(
            text=profile_info["phone"],
            use_logo=True,
        )

        photo = FSInputFile("qr_code.png")

        info = _("Номер бонусной карты: {bonus_card_number}\n\n" "Бонусов: {balance}").format(
            bonus_card_number=profile_info["phone"],
            balance=round(profile_info["walletBalances"][0]["balance"]),
        )

        await bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
        await asyncio.sleep(1)

        await bot.send_photo(
            chat_id=msg.chat.id,
            photo=photo,
            caption=info,
            reply_markup=sell_inline_kb(),
        )

        os.remove("qr_code.png")


@router.message(F.text == __("Пароль от WiFi"), IsAuth())
async def wifi_password_handler(msg: Message, session: AsyncSession):
    await msg.answer(
        _("Мы работаем над установкой Wi-Fi в филиале на Мира. Пароль от него будет здесь в ближайшее " "время 😎")
    )


# Обработка неавторизованных пользователей
@router.message(Command(commands=["balance", "money"]), ~IsAuth())
@router.message(F.text.in_([__("Бонусная карта")]), ~IsAuth())
async def na_profile_handler(msg: Message):
    await msg.answer(
        _(
            "❗Извините, но данное действие доступно только <u>авторизованным</u> пользователям! Пожалуйста, "
            "<b>войдите</b> или <b>создайте</b> аккаунт."
        ),
        reply_markup=auth_kb(),
    )
