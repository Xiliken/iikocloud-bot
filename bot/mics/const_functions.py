# Очистка текста от HTML тэгов
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import User


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


def get_stats(session: AsyncSession) -> dict:
    # Получение пользователей, которые зарегистрированы за сегодня
    reg_users_today = session.scalars(
        select(User).filter(User.registration_date == datetime.date.today())
    )
