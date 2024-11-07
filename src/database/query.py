from .settings import async_session


async def check_user_role(user_id: int):
    async with async_session() as session:
        result = await session.execute()
        existing_user = result.scalars().first()
        return existing_user.role if existing_user else None