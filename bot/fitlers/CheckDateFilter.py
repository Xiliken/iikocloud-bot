import re
from datetime import datetime, timedelta

from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _


class CheckDateFilter(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return await self.is_valid_date(message)

    async def is_valid_date(self, msg: Message):
        # Проверяем формат даты с использованием регулярного выражения
        date_pattern = r"^\d{2}\.\d{2}.\d{4}$"
        if not re.match(date_pattern, msg.text):
            return False

        # Пытаемся преобразовать строку в объект datetime
        try:
            date = datetime.strptime(msg.text, "%d.%m.%Y")

            # Получаем текущую дату
            current_date = datetime.now()

            # Вычисляем дату, которая находится на 7 лет раньше от текущей
            seven_years_ago = current_date - timedelta(days=7 * 365)

            # Проверяем, соответствует ли дата условиям
            if date <= seven_years_ago or date >= current_date:
                await msg.answer(
                    _(
                        "Вы не можете ввести дату, которая меньше {old_date}, "
                        "либо больше или равна текущей дате, то есть {current_date}"
                    ).format(
                        old_date=seven_years_ago.strftime("%d.%m.%Y"),
                        current_date=current_date.strftime("%d.%m.%Y"),
                    )
                )
                return False

            return True
        except ValueError:
            return False
