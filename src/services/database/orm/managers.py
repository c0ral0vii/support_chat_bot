from os.path import split
from typing import Any, Dict, List, Optional
from logger.logger import setup_logger
from src.services.database.database import async_session
from src.services.database.models import Manager, UserCategory, Request, User, Message, Rating
from sqlalchemy import delete, select, or_

logger = setup_logger(__name__)


async def create_managers(all_data: Dict[str, Any]) -> None:
    async with async_session() as session:
        try:
            for user_id, data in all_data.items():
                logger.debug(user_id, data)
                manager = Manager(
                    user_id=int(user_id),
                    name=data.get('name')[0],
                    surname=data.get('name')[-1],
                    username=data.get('name')[0],
                    category=UserCategory(data.get('status')),
                )

                session.add(manager)
            await session.commit()
            logger.debug("комит")
        except Exception as e:
            await session.rollback()


async def delete_manager(user_id: int) -> bool:
    async with async_session() as session:
        stmt = select(Manager).where(Manager.user_id == user_id)
        result = await session.execute(stmt)
        manager = result.scalar_one_or_none()

        if manager is None:
            return True

        await session.delete(manager)
        await session.commit()


async def get_managers() -> List[Manager]:
    async with async_session() as session:
        stmt = select(Manager)
        result = await session.execute(stmt)
        managers = result.scalars().all()

        if managers is None:
            return []

        return managers


async def get_manager(user_id: int) -> Manager | Dict[str, Any] | None:
    async with async_session() as session:
        try:
            stmt = select(Manager).where(Manager.user_id == user_id)
            result = await session.execute(stmt)
            manager = result.scalar_one_or_none()
            if manager is None:
                logger.error("Менеджера не существует")
                return {
                    "error": 200,
                    "text": "Not Found"
                }
            return manager
        except Exception as e:
            await session.rollback()
            return None