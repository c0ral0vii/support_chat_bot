import asyncio
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext

from logger.logger import setup_logger
from src.services.export_message.services import ExportMessageService

export_message_router = Router(name="export_messages_router")
logger = setup_logger(__name__)


@export_message_router.callback_query(lambda query: 'export_messages_' in query.data)
async def export_messages(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        export_message = ExportMessageService()
        request_id = callback.data.split("_")[-1]

        asyncio.create_task(export_message.export_messages(request_id=int(request_id), bot=bot, user_id=callback.from_user.id))
    except Exception as e:
        await callback.message.answer("Произошла ошибка либо при запросе никто не писал сообщений =(")
        return