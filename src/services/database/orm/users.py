from typing import Dict, Any

from asyncpg import UniqueViolationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from logger.logger import setup_logger
from src.services.database.database import async_session
from src.services.database.models import User

logger = setup_logger(__name__)


async def create_user(data: Dict[str, Any]) -> User:
    async with async_session() as session:
        try:
            stmt = select(User).where(User.id == data['user_id'])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                logger.info("Данный пользователь уже существует")
                return user

            user = User(
                user_id=data["user_id"],
                username=data.get('username') if data.get("username") else "Не задано",
            )

            session.add(user)

            await session.commit()

            return user

        except IntegrityError as ie:
            logger.error(f"Ошибка при создании пользователя, {ie}")
            await session.rollback()
        except UniqueViolationError as violation_error:
            logger.error(f"Ошибка при создании пользователя, {violation_error}")
            await session.rollback()
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя, {e}")
            await session.rollback()


async def get_user(user_id: int) -> User:
    async with async_session() as session:
        try:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user is None:
                await create_user(
                    {
                        "user_id": user_id,
                    }
                )
            return user
        except Exception as e:
            logger.error(f"Ошибка создания или пользователь уже существует, {e}")
            await session.rollback()