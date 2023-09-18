from aiogram import Bot


async def notify_admin(bot: Bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)
