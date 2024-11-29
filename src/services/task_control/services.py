from logger.logger import setup_logger


class TaskControlService:
    def __init__(self,
                 logger=setup_logger(__name__),):
        self.tasks = {}
        self.logger = logger

    async def add_task(self, task):
        self.tasks.update(task)
        self.logger.debug(self.tasks)

    async def stop_task(self, request_id):
        try:
            self.logger.debug(self.tasks.get(request_id))
            self.tasks.get(request_id).cancel()
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    async def get_task(self, request_id):
        return self.tasks.get(request_id)


TASK_CONTROL_SERVICE = TaskControlService()