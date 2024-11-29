import asyncio
from logger.logger import setup_logger
from src.services.database.orm.managers import create_managers
from src.services.utils.get_managers import get_managers


class UpdateManagerService:
    def __init__(self,
                 logger=setup_logger(__name__),
                 ):
        self.logger = logger
        self.timestamp = [3600, 86400] # 1 h/2h/6h/1 day

    async def start(self):
        try:
            await self._update_managers()

        except Exception as e:
            self.logger.error(e)

    async def _update_managers(self):
        while True:
            try:
                self.logger.info("Приступаем к обновлению менеджеров")
                managers = await get_managers()
                self.logger.debug(managers)
                await create_managers(managers)
                await asyncio.sleep(self.timestamp[-1])
                await self.start()

            except Exception as e:
                self.logger.error(f"Ошибка при обновлении менеджеров - {e}")
                await asyncio.sleep(self.timestamp[-1])
                await self.start()

    async def add_my_time(self, delay: int):
        try:
            self.timestamp.append(int(delay))
        except Exception as e:
            self.logger.error(f"Ошибка изменения времени обновления менеджеров - {e}")
            return
