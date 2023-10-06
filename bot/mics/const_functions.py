# Очистка текста от HTML тэгов
import datetime

from sqlalchemy import func, or_, select

from bot.database import create_async_engine, get_async_session_maker
from bot.database.methods.user import get_users_count
from bot.database.models import Review, User
from bot.mics import Config, iikoserverapi
from services.iikoserver.IikoServer import IikoServer


def clear_html(get_text: str) -> str:
    if get_text is not None:
        if "<" in get_text:
            get_text = get_text.replace("<", "*")
        if ">" in get_text:
            get_text = get_text.replace(">", "*")
    else:
        get_text = ""

    return get_text


# Очистка мусорных символов из списка
def clear_list(get_list: list) -> list:
    while "" in get_list:
        get_list.remove("")
    while " " in get_list:
        get_list.remove(" ")
    while "," in get_list:
        get_list.remove(",")
    while "\r" in get_list:
        get_list.remove("\r")

    return get_list


# Конвертация дней
def convert_day(day: int) -> str:
    day = int(day)
    days = ["день", "дня", "дней"]

    if day % 10 == 1 and day % 100 != 11:
        count = 0
    elif 2 <= day % 10 <= 4 and (day % 100 < 10 or day % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{day} {days[count]}"


# Удаление отступов у текста
def clear_text(get_text: str) -> str:
    if get_text is not None:
        split_text = get_text.split("\n")

        if split_text[0] == "":
            split_text.pop(0)
        if split_text[-1] == "":
            split_text.pop(-1)
        save_text = []

        for text in split_text:
            while text.startswith(" "):
                text = text[1:]

            save_text.append(text)
        get_text = "\n".join(save_text)
    else:
        get_text = ""

    return get_text


async def get_stats() -> dict:
    engine = await create_async_engine(url=Config.get("DATABASE_URL"))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as session:
        # region Статистика пользователей

        # Регистрация за сегодня
        reg_users_today = await session.scalar(
            select(func.count()).filter(func.DATE(User.registration_date) == datetime.date.today()).select_from(User)
        )

        # Регистраций за неделю
        reg_users_week = await session.scalar(
            select(func.count())
            .filter(func.DATE(User.registration_date) >= datetime.date.today() - datetime.timedelta(days=7))
            .select_from(User)
        )
        # Регистраций за месяц
        reg_users_month = await session.scalar(
            select(func.count())
            .filter(func.DATE(User.registration_date) >= datetime.date.today() - datetime.timedelta(days=30))
            .select_from(User)
        )
        # Регистраций за все время
        reg_users_all = await get_users_count()

        # Сколько пользователей заблокировало бота
        bot_blocked = await session.scalar(select(func.count()).filter(User.is_blocked == True))

        # endregion

        # region Статистика отзывов

        # Сколько всего отзывов
        total_reviews = await session.scalar(select(func.count()).select_from(Review))

        # Положительных отзывов
        total_positive_reviews = await session.scalar(
            select(func.count()).filter(or_(Review.food_rating >= 4, Review.service_rating >= 4))
        )
        # Негативных отзывов
        total_negative_reviews = await session.scalar(
            select(func.count()).filter(or_(Review.food_rating < 4, Review.service_rating < 4))
        )
        # Положительных отзывов за заказ
        positive_reviews_order = await session.scalar(select(func.count()).filter(Review.food_rating >= 4))

        # Негативных отзывов за заказ
        negative_reviews_order = await session.scalar(select(func.count()).filter(Review.food_rating < 4))

        # Положительных отзывов за обслуживание
        positive_reviews_service = await session.scalar(select(func.count()).filter(Review.service_rating >= 4))

        # Негативных отзывов за обслуживание
        negative_reviews_service = await session.scalar(select(func.count()).filter(Review.service_rating < 4))

        # Среднее значение отзывов за заказ
        average_rating_order = await session.scalar(select(func.avg(Review.food_rating)))

        # Среднее значение отзывов за обслуживание
        average_rating_service = await session.scalar(select(func.avg(Review.service_rating)))

        # endregion

        # region Статистика дохода
        iiko_server = IikoServer(
            domain=Config.get("IIKOSERVER_DOMAIN"),
            login=Config.get("IIKOSERVER_LOGIN"),
            password=Config.get("IIKOSERVER_PASSWORD"),
        )

        iikoserverapi.get_departments()
        # endregion

    return {
        "reg_users_today": reg_users_today or 0,
        "reg_users_week": reg_users_week or 0,
        "reg_users_month": reg_users_month or 0,
        "reg_users_all": reg_users_all or 0,
        "bot_blocked": bot_blocked or 0,
        "total_reviews": total_reviews or 0,
        "total_positive_reviews": total_positive_reviews or 0,
        "total_negative_reviews": total_negative_reviews or 0,
        "reviews_order_positive": positive_reviews_order or 0,
        "reviews_order_negative": negative_reviews_order or 0,
        "reviews_service_positive": positive_reviews_service or 0,
        "reviews_service_negative": negative_reviews_service or 0,
        "reviews_avg_order_rating": round(average_rating_order, 1) if average_rating_order is not None else 0,
        "reviews_avg_service_rating": round(average_rating_service, 1) if average_rating_service is not None else 0,
    }
