import re
from abc import ABC
from ctypes import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsPhoneNumber(BaseFilter, ABC):
    def __init__(self):
        pass  # Добавить здесь дополнительные параметры, если это необходимо

    async def check(self, message: Message):
        # Простое регулярное выражение для распознавания номеров телефонов.
        # Может потребоваться адаптировать под конкретные требования.
        pattern = r"^((\+7|7|8)+([0-9]){10})$"
        return bool(re.fullmatch(pattern, message.text))

    def __call__(self, message: Message):
        return self.check(message)


