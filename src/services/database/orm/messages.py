from sqlalchemy import select

from src.services.database.database import async_session
from src.services.database.models import Message, Request


async def create_message(request: Request, message: str) -> Message:
    async with async_session() as session:
        new_message = Message(

        )

        session.add(new_message)

        await session.commit()
        return new_message