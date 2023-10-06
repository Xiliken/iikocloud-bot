import datetime

import aiogram.exceptions
import loguru
from aiogram import Bot
from sqlalchemy import update

from bot.database import create_async_engine, get_async_session_maker
from bot.database.methods.user import get_all_users
from bot.database.models import User
from bot.keyboards.inline import rate_last_order_ikb
from bot.mics import Config, iikocloudapi, notify
from bot.mics.const_functions import clear_text


async def check_orders():
    try:
        loguru.logger.info("ЗАПУСКАЮ ПРОВЕРКУ ПОСЛЕДНИХ ЗАКАЗОВ ПОЛЬЗОВАТЕЛЕЙ")
        # Получаем пользователей из БД
        users_db = await get_all_users()
        bot: Bot = Bot(token=Config.get("TELEGRAM_BOT_API_KEY"), parse_mode="HTML")

        # Проверяем последний заказ из iiko
        for user in users_db:
            last_order = iikocloudapi.get_last_order(user_phone=user[0].phone_number)
            last_order_date = user[0].last_order_date

            # Если у пользователя есть заказ в iiko,
            # то сверяем с датой заказа в БД, если она не пуста
            if last_order and last_order["whenClosed"]:
                last_order_datetime = datetime.datetime.strptime(
                    last_order["whenClosed"], "%Y-%m-%d %H:%M:%S.%f"
                ).replace(microsecond=0, second=0)

                # Если у пользователя есть заказ в iiko и он новый,
                # то отправляем сообщение с текстом отзыва
                if last_order_date and last_order_datetime > last_order_date:
                    try:
                        await notify(
                            bot=bot,
                            chat_id=user[0].user_id,
                            message=clear_text(
                                """
                                                   Спасибо, что выбираете Донерс 😎
                                                   Пожалуйста, оцените <b><u>вкус заказанного блюда</u></b> по шкале <b>от 1 до 5</b>.
                                                   Где 5 наивысшая оценка
                                                   """
                            ),
                            reply_markup=rate_last_order_ikb(),
                        )
                        # Обновляем данные в БД
                        await update_user(user[0].user_id, last_order_datetime)
                    except aiogram.exceptions.TelegramBadRequest as e:
                        if e.message.endswith("chat not found"):
                            pass

                # Если у пользователя нет заказа в iiko,
                # то записываем в БД заказ из iiko
                elif last_order:
                    await update_user(user[0].user_id, last_order_datetime)
        loguru.logger.info("ПРОВЕРКА ПОСЛЕДНИХ ЗАКАЗОВ ЗАВЕРШЕНА")
    except aiogram.exceptions.TelegramBadRequest as e:
        if e.message.endswith("chat not found"):
            pass


async def update_user(user_id, last_order_datetime):
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as conn:
        await conn.execute(update(User).where(User.user_id == user_id).values(last_order_date=last_order_datetime))
        await conn.commit()
