import datetime
import os
import zipfile

import loguru
from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile
from aiogram.utils.i18n import I18n

from bot.mics import Config


async def backup(bot: Bot, i18n: I18n):
    try:
        await bot.send_chat_action(chat_id=Config.get("NOTIFY_ADMIN_IDS", "int"), action=ChatAction.TYPING)
        await bot.send_message(
            chat_id=Config.get("NOTIFY_ADMIN_IDS", "int"),
            text=i18n.gettext(
                "Начинаю создание резервной копии БД!\n\n"
                "ℹ️ Если бот не отослал сообщение в течении 1 минуты, беги смотреть логи!"
            ),
        ),

        with zipfile.ZipFile(
            f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip", "w", compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            zip_file.write("database.db")
            zip_file.comment = b"{date}".replace(
                b"{date}", bytes(f'Резервная копия от: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', "utf-8")
            )

        await bot.send_document(
            chat_id=Config.get("NOTIFY_ADMIN_IDS", "int"),
            document=FSInputFile(path=f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip"),
            caption=i18n.gettext("Резервная копия БД от {date}").format(
                date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            ),
        )
        os.remove(f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip")

        loguru.logger.success("Резервная копия БД успешно завершена!")
    except Exception as e:
        loguru.logger.error(f"Не удалось создать или отправить резервную копию БД!\n{e}")
        os.remove(f"backup_{datetime.datetime.now().strftime('%Y-%d-%m')}.zip")
        await bot.send_message(
            chat_id=Config.get("NOTIFY_ADMIN_IDS", "int"),
            text=i18n.gettext("🔴 Не удалось создать или отправить резервную копию БД! Бегом смотреть логи!"),
        )
