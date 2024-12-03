from app.application.services.generation.retry import retry_expired_jobs
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.task.base import AsyncTaskManager


class RetryTaskManager(AsyncTaskManager):
    def __init__(
            self,
            rabbit_mq_service: RabbitMQService,
            check_interval: int = 60
    ):
        super().__init__(check_interval)
        self.rabbit_mq_service = rabbit_mq_service

    async def execute(self):
        await retry_expired_jobs(rabbit_mq_service=self.rabbit_mq_service)