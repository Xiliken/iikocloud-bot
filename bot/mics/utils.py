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
