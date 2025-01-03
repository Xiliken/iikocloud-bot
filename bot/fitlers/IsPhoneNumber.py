import re
from abc import ABC

from aiogram.filters import BaseFilter
from aiogram.types import Message


def normalize_phone_number(phone: str):
    # Удалить все символы, кроме цифр
    cleaned_phone = re.sub(r"\D", "", phone)

    # Если номер начинается с "8", заменить его на "+7"
    if cleaned_phone.startswith("8"):
        cleaned_phone = "7" + cleaned_phone[1:]

    # Если номер короткий (без кода страны), добавить "+7" в начало
    if len(cleaned_phone) == 10:
        cleaned_phone = "7" + cleaned_phone

    return cleaned_phone


async def check_message(message: Message):
    # Простое регулярное выражение для распознавания номеров телефонов.
    # Может потребоваться адаптировать под конкретные требования.
    pattern = r"^((\+7|7|8)+([0-9]){10})$"
    return bool(re.fullmatch(pattern, normalize_phone_number(message.text)))


class IsPhoneNumber(BaseFilter, ABC):
    def __init__(self):
        pass  # Добавить здесь дополнительные параметры, если это необходимо

    def __call__(self, message: Message):
        return check_message(message)
