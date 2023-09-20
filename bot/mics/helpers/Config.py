import ast
from os import getenv
from typing import Dict, List, Union

import dotenv
from dotenv import find_dotenv, load_dotenv


class Config:
    @staticmethod
    def get(
        key: str, value_type: str = "str"
    ) -> Union[str, bool, List[str], Dict[str, str], int, float, None]:
        # Загрузка env
        load_dotenv(find_dotenv())
        value = getenv(str(key))

        if value is not None:
            if value_type == "str":
                return str(value)
            elif value_type == "bool":
                return value.lower() == "true"
            elif value_type == "list":
                return ast.literal_eval(value)
            elif value_type == "dict":
                return dict(item.split("=") for item in value.split(","))
            elif value_type == "int":
                return int(value)
            elif value_type == "float":
                return float(value)

        return None

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
        dotenv.set_key(".env", key, value)
