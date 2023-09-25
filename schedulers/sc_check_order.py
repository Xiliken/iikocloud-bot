import datetime
from typing import Union

from aiogram import Bot
from aiogram.utils.i18n import FSMI18nMiddleware, I18n, SimpleI18nMiddleware
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import update

from bot.database import create_async_engine, get_async_session_maker
from bot.database.methods.orders import get_last_order_date
from bot.database.models import User
from bot.keyboards.inline import rate_last_order_ikb
from bot.mics import Config, iikoapi, notify


async def sc_check_order(user_id, phone: Union[str, int]) -> bool:
    """
    Проверка времени последнего заказа пользователя
    :return:
    """

    bot: Bot = Bot(token=Config.get("TELEGRAM_BOT_API_KEY"), parse_mode="HTML")
    # TODO: Продумать, как можно от этого избавиться
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    # Последний заказ из iiko
    last_order_iiko = iikoapi.get_last_order(user_phone=phone)

    last_order_iiko_datetime = datetime.datetime.strptime(
        last_order_iiko["whenClosed"], "%Y-%m-%d %H:%M:%S.%f"
    ).replace(microsecond=0, second=0)

    # Получение времени последнего заказа пользователя из базы данных
    last_order_date_db = await get_last_order_date(phone=phone)

    if last_order_date_db is None:
        # Если у пользователя нет в бд последнего заказа, то нужно записать его
        # из iiko
        async with session_maker.begin() as conn:
            if last_order_iiko is None:
                await conn.execute(
                    update(User)
                    .where(User.user_id == user_id)
                    .values(last_order_date=last_order_iiko_datetime)
                )
                await conn.commit()

    last_order_db_datetime = datetime.datetime.strptime(
        last_order_date_db, "%Y-%m-%d %H:%M"
    )

    # Обновляем данные о последнем заказе
    if last_order_iiko_datetime > last_order_db_datetime:
        await notify(
            bot=bot,
            chat_id=user_id,
            message="Спасибо, что выбираете Донерс 😎\n"
            "Пожалуйста, оцените вкус заказанного блюда по шкале от 1 до 5."
            "Где 5 наивысшая оценка",
            reply_markup=rate_last_order_ikb(),
        )
