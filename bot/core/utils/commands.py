from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='menu',
            description='Главное меню'
        ),
        BotCommand(
            command='pari',
            description='Мои пари'
        ),
        BotCommand(
            command='profile',
            description='Профиль'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
