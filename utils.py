from aiogram.types import BotCommand

commands_admin = [
    BotCommand(
        command='start',
        description='Start/restart bot'
    ),
    BotCommand(
        command='contest_list',
        description='all users with ID'
    ),
   ]


commands_user = [
    BotCommand(
        command='start',
        description='Start/restart bot'
    )]