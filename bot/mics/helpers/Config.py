from os import getenv

import dotenv
from dotenv import load_dotenv, find_dotenv


class Config:
    @staticmethod
    def get(key: str) -> str:
        # Загрузка env
        load_dotenv(find_dotenv())
        return getenv(str(key))

    @staticmethod
    def set(key: str, value: any):
        import os
        if isinstance(value, str):
            value = f'"{value}"'
        else:
            value = str(value)

        # Обновление переменной окружения
        os.environ[key] = value

        # Обновление в файле
        dotenv.set_key('.env', key, value)