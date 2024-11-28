from logger.logger import setup_logger
from src.services.database.database import async_session
from src.services.database.orm.create_request import get_request
from src.services.database.models import Rating


logger = setup_logger(__name__)


async def set_rating(rating: int, request_id: int) -> bool:
    request = await get_request(request_id=request_id, full_model=True)
    if not request:
        logger.critical(f'Не удалось найти запрос - {request_id}')
        return False

    async with async_session() as session:
        new_rating = Rating(
            request_id=request_id,
            rating_value=int(rating),
        )

        session.add(new_rating)
        await session.commit()