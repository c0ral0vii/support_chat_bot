import asyncio
from aiogram import Bot, Dispatcher, types
from src.services.config.config import settings
from src.services.bot.handlers import (
    client
)

bot = Bot(token=settings.get_bot_token())
dp = Dispatcher()

dp.include_routers(
    client.client_router,
)


async def on_startup():
    commands = [
        types.BotCommand(command="/start", description="Запуск бота"),
        types.BotCommand(command="/cancel", description="Отменить действие"),
        types.BotCommand(command="/back", description="Назад")
    ]
    await bot.set_my_commands(commands)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup()
    print("Started")
    await dp.start_polling(bot)

asyncio.run(main())