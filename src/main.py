import asyncio
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from handlers.client import client_router
from handlers.executive_director import executive_director

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_routers(client_router, executive_director)

async def on_startup(dp):
    commands = [
        types.BotCommand(command="/start", description="Запуск бота"),
        types.BotCommand(command="/cancel", description="Отменить действие"),
        types.BotCommand(command="/back", description="Назад")
    ]
    await bot.set_my_commands(commands)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup(dp)
    print("Started")
    await dp.start_polling(bot)

asyncio.run(main())
