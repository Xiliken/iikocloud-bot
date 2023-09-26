import loguru
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from bot.database.methods.user import get_admins

user_commands = [
    BotCommand(command="start", description="Запустить бота"),
    # BotCommand(
    #     command='help',
    #     description='Помощь по боту'
    # ),
    BotCommand(command="balance", description="Мои бонусы"),
    BotCommand(command="contacts", description="Контакты организации"),
    # BotCommand(
    #     command='sales',
    #     description='Доступные акции'
    # ),
    BotCommand(command="chat", description="Чат с оператором"),
    BotCommand(command="register", description="Создать аккаунт"),
    BotCommand(command="login", description="Войти в аккаунт"),
]


admin_commands = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="chat", description="Чат с оператором"),
    BotCommand(command="register", description="Создать аккаунт"),
    BotCommand(command="login", description="Войти в аккаунт"),
    BotCommand(command="balance", description="Мои бонусы"),
    BotCommand(command="contacts", description="Контакты организации"),
    BotCommand(command="admin", description="Войти в панель администратора"),
    BotCommand(command="stats", description="Просмотреть статистику"),
    BotCommand(command="broadcast", description="Рассылка сообщений пользователям"),
]


async def set_commands(bot: Bot) -> None:
    await bot.set_my_commands(user_commands, BotCommandScopeDefault())

    admins_list = await get_admins()

    if len(admins_list) != 0:
        for admin in await get_admins():
            try:
                await bot.set_my_commands(
                    admin_commands, scope=BotCommandScopeChat(chat_id=admin[0].user_id)
                )
            except Exception as e:
                loguru.logger.error(e)
