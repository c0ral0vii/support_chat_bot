from typing import Any, Dict
from logger.logger import setup_logger
from src.services.database.database import get_session
from src.services.database.models import User, Manager
from sqlalchemy import delete, select

logger = setup_logger(__name__)


async def create_managers(all_data: Dict[str, Any]) -> None:
    async with get_session() as session:
        try:
            for user_id, data in all_data.items():
                manager = Manager(
                    user_id=int(user_id),
                    name=data['name'],
                    surname=data['surname'],
                    username=data['username'],
                    category=data['category'],
                )

                session.add(manager)

            await session.commit()
        except Exception as e:
            logger.error(f"Ошибка при добавлении менеджера - {e}")
            session.rollback()


async def delete_manager(user_id: int) -> bool:
    async with get_session() as session:
        stmt = select(Manager).where(Manager.user_id == user_id)
        result = await session.execute(stmt)
        manager = result.scalar_one_or_none()

        if manager is None:
            return True

        await session.delete(manager)
        await session.commit()