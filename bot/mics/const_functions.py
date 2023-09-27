# Очистка текста от HTML тэгов
import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import create_async_engine, get_async_session_maker
from bot.database.methods.user import get_all_users, get_users_count
from bot.database.models import User
from bot.mics import Config


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
        # Регистрация за сегодня
        reg_users_today = await session.scalar(
            select(func.count())
            .filter(User.registration_date == datetime.date.today())
            .select_from(User)
        )
        # Регистраций за неделю
        reg_users_week = await session.scalar(
            select(func.count())
            .filter(
                User.registration_date
                >= datetime.date.today() - datetime.timedelta(days=7)
            )
            .select_from(User)
        )
        # Регистраций за месяц
        reg_users_month = await session.scalar(
            select(func.count())
            .filter(
                User.registration_date
                >= datetime.date.today() - datetime.timedelta(days=30)
            )
            .select_from(User)
        )
        # Регистраций за все время
        reg_users_all = await get_users_count()

        # Сколько пользователей заблокировало бота
        bot_blocked = await session.scalar(
            select(func.count()).filter(User.is_blocked == True)
        )

    return {
        "reg_users_today": reg_users_today,
        "reg_users_week": reg_users_week,
        "reg_users_month": reg_users_month,
        "reg_users_all": reg_users_all,
        "bot_blocked": bot_blocked,
    }
