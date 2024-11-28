import asyncio
from aiogram import Bot, Dispatcher, types

from src.services.config.config import settings
from src.services.bot.handlers import (
    client,
    clo_manager,
    subcategory_handler,
    messages_handler,
    rating_handler,

    executive_director,
    senior_clo_manager,
)

from src.services.update_managers.service import UpdateManagerService


bot = Bot(token=settings.get_bot_token)
dp = Dispatcher()

dp.include_routers(
    client.client_router,
    clo_manager.clo_manager_router,
    subcategory_handler.subcategory_router,
    messages_handler.message_router,
    rating_handler.rating_router,

    executive_director.executive_director_router,
    senior_clo_manager.senior_clo_router,
)


async def on_startup():
    commands = [
        types.BotCommand(command="/start", description="Запуск бота / Создать запрос"),
    ]
    await bot.set_my_commands(commands)


async def main():
    asyncio.create_task(UpdateManagerService().start())
    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup()
    print("Started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())