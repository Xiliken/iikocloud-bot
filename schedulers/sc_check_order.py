import datetime
from typing import Union

from aiogram import Bot

from bot.database.methods.orders import get_last_order_date
from bot.mics import iikoapi


async def sc_check_order(user_id, phone: Union[str, int], bot: Bot):
    """
    Проверка времени последнего заказа пользователя
    :return:
    """

    last_order_date_db = await get_last_order_date(
        phone=phone
    )  # Получение времени последнего заказа пользователя из базы данных
    last_order_iiko = iikoapi.get_last_order(user_phone=phone)

    last_order_iiko_datetime = datetime.datetime.strptime(
        last_order_iiko["whenClosed"], "%Y-%m-%d %H:%M:%S.%f"
    ).replace(microsecond=0, second=0)

    last_order_db_datetime = datetime.datetime.strptime(
        last_order_date_db, "%Y-%m-%d %H:%M"
    )

    if last_order_iiko is None:
        return

    if last_order_date_db is None:
        # Если у пользователя нет в бд последнего заказа, то нужно записать его
        # из iiko
        return

    print(
        f"Результат проверки времени последнего заказа пользователя: {last_order_iiko_datetime > last_order_db_datetime}"
    )

    print(bot)
    if last_order_iiko_datetime > last_order_db_datetime:
        await bot.send_message(chat_id=user_id, text="Работает")
    else:
        await bot.send_message(chat_id=user_id, text="НЕ работает")
