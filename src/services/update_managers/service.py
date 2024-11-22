import asyncio
from logger.logger import setup_logger
from src.services.database.orm.managers import create_managers
from src.services.database.models import UserCategory
from src.services.utils.get_managers import get_managers


class UpdateManagerService:
    def __init__(self,
                 logger=setup_logger(__name__),
                 ):
        self.logger = logger
        self.timestamp = [30, 60, 120, 240, 360]

    async def start(self):
        try:
            asyncio.create_task(self._update_managers())

        except Exception as e:
            self.logger.error(e)

    async def _update_managers(self):
        while True:
            try:
                self.logger.info("Приступаем к обновлению менеджеров")
                managers = await get_managers()
                await create_managers(managers)

            except Exception as e:
                self.logger.error(f"Ошибка при обновлении менеджеров - {e}")

