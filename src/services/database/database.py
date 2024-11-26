from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from logger.logger import setup_logger
from src.services.config.config import settings

logger = setup_logger(__name__)
DATABASE_URL = "postgresql+asyncpg://root:root@0.0.0.0:5432/support_db"
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_session():
    async with async_session() as session:
        yield session

