import re


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

