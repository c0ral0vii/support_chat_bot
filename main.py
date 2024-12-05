import asyncio
from aiogram import Bot, Dispatcher, types

from src.services.bot.handlers.vacation_handler import vacation_router
from src.services.config.config import settings
from src.services.bot.handlers import (
    client,
    clo_manager,
    subcategory_handler,
    messages_handler,
    rating_handler,
    export_messages_handler,
    vacation_handler,

    executive_director,
    senior_clo_manager,
)

from src.services.update_managers.service import UpdateManagerService
from src.services.statistic.services import stats_service

bot = Bot(token=settings.get_bot_token)
dp = Dispatcher()

dp.include_routers(
    client.client_router,
    clo_manager.clo_manager_router,
    subcategory_handler.subcategory_router,
    messages_handler.message_router,
    rating_handler.rating_router,
    export_messages_handler.export_message_router,

    vacation_handler.vacation_router,
    executive_director.executive_director_router,
    senior_clo_manager.senior_clo_router,
)


async def on_startup():
    commands = [
        types.BotCommand(command="/start", description="Запуск бота / Создать запрос"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await stats_service.start()
    update_manager = UpdateManagerService()
    asyncio.create_task(update_manager.start())
    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup()
    print("Started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())