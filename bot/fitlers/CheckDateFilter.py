import re
from datetime import datetime

from aiogram.filters import BaseFilter
from aiogram.types import Message


class CheckDateFilter(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return self.is_valid_date(message)

    def is_valid_date(self, msg: Message):
        # Проверяем формат даты с использованием регулярного выражения
        date_pattern = r'^\d{2}\.\d{2}.\d{4}$'
        if not re.match(date_pattern, msg.text):
            return False

        # Пытаемся преобразовать строку в объект datetime
        try:
            datetime.strptime(msg.text, '%d.%m.%Y')
            return True
        except ValueError:
            return False
