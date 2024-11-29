from typing import Dict, Any

from sqlalchemy import select

from src.services.database.database import async_session
from src.services.database.models import Message, Request


async def create_message(request: Request, data: Dict[str, Any]) -> Message:
    async with async_session() as session:
        new_message = Message(
            from_=data['from'],
            request_id=data.get('request_id'),
            message=data.get("message"),
        )

        session.add(new_message)

        await session.commit()
        return new_message