from typing import Dict, Any
from sqlalchemy import select, asc

from logger.logger import setup_logger
from src.services.database.database import async_session
from src.services.database.models import Request, Message, Manager, User


logger = setup_logger(__name__)


async def get_messages(request_id: int) -> Dict[str, Any]:
    async with async_session() as session:
        try:
            stmt = select(Message).where(Message.request_id == request_id).order_by(asc(Message.created)) # сортировка по времени
            result = await session.execute(stmt)
            messages = result.scalars().all()

            return messages

        except Exception as e:
            logger.error(f"Ошибка при выгрузке сообщений - {e}")
            return {
                "error": 404,
                "text": "Не удалось выгрузить переписку",
            }
