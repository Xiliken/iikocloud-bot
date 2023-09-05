from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(
            command='start',
            description='Запустить бота'
        ),
        BotCommand(
            command='help',
            description='Помощь по боту'
        ),
        BotCommand(
            command='balance',
            description='Мои бонусы'
        ),
        BotCommand(
            command='contacts',
            description='Контакты организации'
        ),
        BotCommand(
            command='sales',
            description='Доступные акции'
        ),
        BotCommand(
            command='chat',
            description='Чат с оператором'
        ),
        BotCommand(
            command='register',
            description='Создать аккаунт'
        ),
        BotCommand(
            command='login',
            description='Войти в аккаунт'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
