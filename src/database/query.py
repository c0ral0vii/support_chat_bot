from .settings import async_session
from .models import Request, User, Client


async def check_user_role(user_id: int):
    async with async_session() as session:
        result = await session.execute()
        existing_user = result.scalars().first()
        return existing_user.role if existing_user else None


async def create_user(user_id: int, username: str, category: str) -> int:
    async with async_session() as session:
        user = User(
            user_id=user_id,
            username=username,
            category=category,
        )

        session.add(user)
        session.commit()


async def create_request(user_id: int, manager_id: int, category: str) -> int:
    async with async_session() as session:
        user = session.execute()
        manager_id = manager_id

        request = Request(
            user_id=user,
            client_id=manager_id,
            category=category
        )

        session.add(request)
        session.commit()
