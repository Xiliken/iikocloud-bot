import re


# def config(key: str) -> str:
#     from os import getenv
#     from dotenv import load_dotenv, find_dotenv
#
#     # Загрузка env
#     load_dotenv(find_dotenv())
#
#     return getenv(str(key))
#
# def set_config(key: str, val: any):
#     import os
#     os.environ[key] = val


# Проверка номера телефона
def check_phone_number(phone: str) -> bool:
    regex = r"^\+7\d{10}$"
    if not re.match(regex, phone):
        return False
    return True


def registration(phone_number: str):
    pass


def log(message) -> None:
    import logging
    logging.basicConfig(filename='errors.log', level=logging.ERROR)
    logging.error(message)


def normalize_phone_number(phone: str) -> str:
    # Удалить все символы, кроме цифр
    cleaned_phone = re.sub(r'\D', '', phone)

    # Если номер начинается с "8", заменить его на "+7"
    if cleaned_phone.startswith('8'):
        cleaned_phone = '7' + cleaned_phone[1:]

    # Если номер короткий (без кода страны), добавить "+7" в начало
    if len(cleaned_phone) == 10:
        cleaned_phone = '7' + cleaned_phone

    return cleaned_phone
