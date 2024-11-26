from typing import Dict, Any

from sqlalchemy import select

from logger.logger import setup_logger
from src.services.database.database import async_session
from src.services.database.models import User

logger = setup_logger(__name__)


async def create_user(data: Dict[str, Any]) -> User:
    async with async_session() as session:
        try:
            user = User(
                user_id=data["user_id"],
                username=data.get('username') if data.get("username") else "Не задано",
            )

            session.add(user)

            await session.commit()

            return user

        except Exception as e:
            logger.error("Ошибка при создании пользователя")
            await session.rollback()


async def get_user(user_id: str) -> User:
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
            logger.error("Ошибка создания или пользователь уже существует")
            await session.rollback()