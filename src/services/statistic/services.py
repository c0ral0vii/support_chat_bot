import asyncio

from logger.logger import setup_logger


class StatisticService:
    def __init__(self,
                 logger=setup_logger(__name__)):
        self.logger = logger
        self.timeout = [30, 60]
    async def start(self):
        try:
            ...
        except Exception as e:
            self.logger.error(e)
            await asyncio.sleep(self.timeout[1])


    async def get_month(self):
        ...


    async def _set_update(self):
        ...