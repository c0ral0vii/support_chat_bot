from typing import Any, Dict, NoReturn

from sqlalchemy import select
from urllib3 import request

from logger.logger import setup_logger
from src.services.database.orm.users import get_user
from src.services.database.orm.managers import get_manager
from src.services.database.database import async_session
from src.services.database.models import Request, User, Manager, RequestCategory, RequestSubCategory

logger = setup_logger(__name__)


async def create_request(data: Dict[str, Any]) -> Request:
    async with async_session() as session:
        try:
            user = await get_user(data["user_id"])
            # manager = await get_manager(data["manager_id"])

            logger.debug(f"{user.user_id}")

            new_request = Request(
                user_id=user.user_id,
                contact_number_or_inn=data["contact_number_or_inn"],
                manager_id=None,
                request_category=RequestCategory(data.get("status")),
                close=False,
            )

            session.add(new_request)

            await session.commit()

            return new_request
        except Exception as e:
            print(e)
            await session.rollback()


async def accept_request(request_id: int, manager_id: int) -> Request | dict:
    async with async_session() as session:
        try:
            stmt = select(Request).where(Request.id == request_id)
            result = await session.execute(stmt)
            request = result.scalar_one_or_none()
            manager = await get_manager(manager_id)
            if request.manager_id:
                return {
                    "error": "Заказ уже принят",
                    "manager_id": request.manager_id,
                }

            request.manager_id = manager.user_id

            await session.commit()
            return request
        except Exception as e:
            logger.error(f"Не удалось взять реквест - {e}")


async def get_request(request_id: int, full_model: bool = False) -> dict[str, Any] | None | Request:
    async with async_session() as session:
        stmt = select(Request).where(Request.id == request_id)
        result = await session.execute(stmt)
        request = result.scalar_one_or_none()

        if not request:
            return None

        if full_model:
            return request

        return {
            "request_id": request.id,
            "request_manager": request.manager_id,
            "request_status": request.close,
            "request_user_id": request.user_id,
        }


async def close_request_status(request_id: int) -> dict:
    async with async_session() as session:
        stmt = select(Request).where(Request.id == request_id)
        result = await session.execute(stmt)
        request = result.scalar_one_or_none()

        if not request:
            return {
                "status": 404,
            }

        request.close = True

        await session.commit()

        return {
            "status": 200,
            "request_id" : request.id,
            "request_status": request.close
        }


async def change_subcategory(request_id: int, subcategory: RequestSubCategory) -> NoReturn:
    request = await get_request(request_id, full_model=True)
    async with async_session() as session:
        try:
            request.subcategory = RequestSubCategory(subcategory)

            await session.commit()
        except Exception as e:
            logger.debug(e)
            await session.rollback()