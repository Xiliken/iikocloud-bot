import re
import time

from aiogram import Bot
from aiogram.types import Message

from bot.mics.helpers.Config import Config
from bot.mics.notify_admin import notify_admin


def normalize_phone_number(phone: str) -> str:
    """
    Нормализация телефонного номера
    :param phone: Номер телефона
    :return: Нормализованный номер телефона в формате 7xxxxxxxxxx
    """

    # Удалить все символы, кроме цифр
    cleaned_phone = re.sub(r'\D', '', phone)

    # Если номер начинается с "8", заменить его на "+7"
    if cleaned_phone.startswith('8'):
        cleaned_phone = '7' + cleaned_phone[1:]

    # Если номер короткий (без кода страны), добавить "+7" в начало
    if len(cleaned_phone) == 10:
        cleaned_phone = '7' + cleaned_phone

    return cleaned_phone


async def check_telegram_account_exists(message: Message = Message) -> bool:
    """
    Проверка, зарегистрирован ли такой пользователь уже в боте
    :param message: Объект сообщения aiogram
    :return: bool
    """
    from bot.database import create_async_engine, get_async_session_maker

    engine = await create_async_engine(url=Config.get('DATABASE_URL'))
    session_maker = get_async_session_maker(engine)

    async with session_maker.begin() as conn:
        phone = message.text or message.contact.phone_number

        from sqlalchemy import select
        from bot.database.models import User
        user = await conn.scalars(
            select(User)
            .where(User.phone_number == normalize_phone_number(phone) )
            .where(User.user_id != message.from_user.id)
        )
        user = user.first()

        return bool(user)


def read_changelog():
    with open('changelog'.upper(), "r") as file:
        return file.read()


async def check_changelog(bot: Bot, chat_id):
    current_content = read_changelog()
    while True:
        time.sleep(1)
        new_content = read_changelog()

        if new_content != current_content:
            diff = "Вышло новое обновление!\n\n{}".format(new_content)
            await notify_admin(bot, chat_id, diff)
            current_content = new_content







