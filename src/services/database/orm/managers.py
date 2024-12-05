from datetime import datetime
from os.path import split
from typing import Any, Dict, List, Optional
from logger.logger import setup_logger
from src.services.database.database import async_session
from src.services.database.models import Manager, UserCategory, Request, User, Message, Rating
from sqlalchemy import delete, select, or_, and_
from sqlalchemy.exc import IntegrityError


logger = setup_logger(__name__)


async def create_managers(all_data: Dict[str, Any]) -> None:
    async with async_session() as session:
        try:
            for user_id, data in all_data.items():
                logger.debug(user_id, data)
                try:
                    stmt = select(Manager).where(or_(
                        Manager.username == user_id,
                        and_(Manager.surname == data['name'][-1], Manager.name == data['name'][0])
                    ))

                    result = await session.execute(
                        stmt
                    )
                    existing_manager = result.scalar_one_or_none()

                    if existing_manager:
                        existing_manager.user_id = int(user_id)
                        existing_manager.username = user_id
                        logger.debug(f"Manager with username {data.get('username', '@')} already exists. Skipping.")
                        continue

                    manager = Manager(
                        user_id=int(user_id),
                        name=data.get('name')[0],
                        field=data.get('field'),
                        surname=data.get('name')[-1],
                        username=user_id,
                        category=UserCategory(data.get('status')),
                    )

                    session.add(manager)
                    await session.commit()
                except IntegrityError as e:
                    logger.debug(f"IntegrityError: {e}")
                    await session.rollback()
                    continue
                except Exception as e:
                    logger.debug(f"Exception: {e}")
                    await session.rollback()
                    continue
            logger.debug("Commit successful")
        except Exception as e:
            logger.debug(f"Exception: {e}")
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
                return {
                    "error": 200,
                    "text": "Not Found"
                }
            
            return manager
        except Exception as e:
            await session.rollback()
            return None


async def set_vacation(user_id: int, data: Dict[str, Any], **kwargs):
    manager = await get_manager(user_id=user_id)
    async with async_session() as session:
        try:
            manager.vacation_start = datetime.strptime(data["from_"], "%d.%m.%Y")
            manager.vacation_end = datetime.strptime(data["to_"], "%d.%m.%Y")
            manager.number = str(data.get("phone", 'XX'))

            session.add(manager)
            await session.commit()
        except Exception as e:
            await session.rollback()


async def disable_vacation(user_id: int):
    manager = await get_manager(user_id=user_id)
    async with async_session() as session:
        try:
            manager.vacation_start = None
            manager.vacation_end = None
            manager.number = None

            session.add(manager)
            await session.commit()
        except Exception as e:
            await session.rollback()