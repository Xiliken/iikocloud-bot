import hashlib
import os
import re
import time
from datetime import datetime

from aiogram import Bot

from bot.mics import notify_admin


def read_changelog():
    with open('changelog'.upper(), "r") as file:
        return file.read()


async def check_changelog(bot: Bot, chat_id):
    while True:
        # Получить последнее время изменения файла changelog
        changelog_path = 'changelog'.upper()
        last_modified = os.path.getmtime(changelog_path)

        # Ждать некоторое время, чтобы убедиться, что файл не изменяется
        time.sleep(2)

        # Проверить, изменился ли файл changelog
        if os.path.getmtime(changelog_path) > last_modified:
            # Если файл изменился, прочитать его содержимое
            with open(changelog_path, 'r', encoding='utf8') as file:
                content = file.read()

            # Найти все записи в файле с помощью регулярного выражения
            entries = re.findall(r'\d+\.\d+\.\d+ \(\d{2}/\d{2}/\d{4}\)\n-*\n.*', content)

            if entries:
                # Получить последнюю запись
                latest_entry = entries[-1]

                # Извлечение версии и даты с помощью регулярного выражения
                version_date = re.search(r'(\d+\.\d+\.\d+) \((\d{2}/\d{2}/\d{4})\)', latest_entry)
                version = version_date.group(1)
                date = datetime.strptime(version_date.group(2), '%m/%d/%Y').strftime('%d.%m.%Y')

                # Извлечение изменений
                changes = '\n'.join(latest_entry.split('\n')[2:])

                # Форматирование текста сообщения
                message = f'Вышло новое обновление:\nВерсия: {version} ({date})\n{changes}'

                await notify_admin(bot=bot, chat_id=chat_id, message=message)