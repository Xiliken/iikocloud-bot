# Очистка текста от HTML тэгов
import calendar
import datetime

from sqlalchemy import and_, func, or_, select

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

        # Текущий день
        current_date = datetime.datetime.today()

        # Получить первый день текущего месяца
        first_day_of_month = datetime.date(current_date.year, current_date.month, 1)

        # Получить последний день текущего месяца
        last_day_of_month = datetime.date(
            current_date.year, current_date.month, calendar.monthrange(current_date.year, current_date.month)[1]
        )

        # Регистраций за месяц
        reg_users_month = await session.scalar(
            select(func.count())
            .filter(
                and_(
                    func.DATE(User.registration_date) >= first_day_of_month,
                    func.DATE(User.registration_date) <= last_day_of_month,
                )
            )
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
            select(func.count()).filter(
                and_(
                    Review.food_rating <= 3,
                    Review.food_rating != 0,
                )
            )
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

        departments = iikoserverapi.get_departments()
        department_incomes = []

        # Формирование доходов
        for department in departments:
            # Получить доход за сегодня
            income_today = _get_income_stats(
                iiko_server.sales(
                    department=department["id"],
                    date_from=datetime.datetime.now().strftime("%d.%m.%Y"),
                    date_to=datetime.datetime.now().strftime("%d.%m.%Y"),
                )
            )

            # Получить доход за вчера
            income_yesterday = _get_income_stats(
                iiko_server.sales(
                    department=department["id"],
                    date_from=(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d.%m.%Y"),
                    date_to=(datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d.%m.%Y"),
                )
            )

            # Получить доход за неделю
            income_per_week = _get_income_stats(
                iiko_server.sales(
                    department=department["id"],
                    date_from=(datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%d.%m.%Y"),
                    date_to=datetime.datetime.now().strftime("%d.%m.%Y"),
                )
            )

            department_incomes.append(
                {
                    "department_id": department["id"],
                    "department_name": department["name"],
                    "income_today": income_today,
                    "income_yesterday": income_yesterday,
                    "income_per_week": income_per_week,
                }
            )

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
        "department_incomes": department_incomes,
    }


def _get_income_stats(xml):
    """
    Получить статистику доходов за периоды
    :return:
    """
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml)

    day_dish_values = root.findall("dayDishValue")

    if not day_dish_values:
        return 0

    # Если есть несколько дат, то считаем их сумму

    if len(day_dish_values) > 1:
        total_income = 0
        for day_dish_value in day_dish_values:
            total_income += float(day_dish_value.find("value").text)
        return round(total_income, 2)

    # Если одна дата, то просто возвращаем ее значение

    return float(day_dish_values[0].find("value").text)
