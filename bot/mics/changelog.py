import os
import re
import time
from datetime import datetime

from aiogram import Bot
from loguru import logger

from bot.mics import notify_admin


async def check_changelog(bot: Bot):
    # Получить последнее время изменения файла changelog
    changelog_path = "changelog".upper()
    last_modified = os.path.getmtime(changelog_path)

    # Ждать некоторое время, чтобы убедиться, что файл не изменяется
    time.sleep(2)

    # Проверить, изменился ли файл changelog
    if os.path.getmtime(changelog_path) > last_modified:
        # Если файл изменился, прочитать его содержимое
        with open(changelog_path, "r", encoding="cp1251") as file:
            content = file.read()

        # Найти все записи в файле с помощью регулярного выражения
        entries = re.findall(
            r"(\d+\.\d+\.\d+) \((\d{2}/\d{2}/\d{4})\)\n[-]+\n(.+?)(?=\n+\d+\.\d+\.\d+ \(\d{2}/\d{2}/\d{4}\)\n[-]+\n|$)",
            content,
            re.DOTALL,
        )

        if entries:
            # Получить последнюю запись
            latest_entry = entries[-1]

            # Извлечение версии и даты
            version = latest_entry[0]
            date_str = latest_entry[1]

            # Преобразование даты в правильный формат
            date = datetime.strptime(date_str, "%m/%d/%Y").strftime("%d.%m.%Y")

            # Извлечение изменений
            changes = latest_entry[2].strip()

            # Форматирование текста сообщения
            message = f"<b>Вышло новое обновление</b>:\n\n<u>Версия</u>: {version} ({date})\n\n{changes}"

            await notify_admin(bot=bot, chat_id=5599795627, message=message)

            logger.info(
                "Сhangelog has been updated. A notification of changes has been sent to Telegram!"
            )
