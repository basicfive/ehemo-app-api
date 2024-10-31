from app.application.services.generation.retry import ImageGenerationRetryService
from app.infrastructure.task.base import AsyncTaskManager


class RetryTaskManager(AsyncTaskManager):
    def __init__(
            self,
            retry_service: ImageGenerationRetryService,
            check_interval: int = 60
    ):
        super().__init__(check_interval)
        self.retry_service = retry_service

    async def execute(self):
        """재시도 로직 실행"""
        await self.retry_service.retry_expired_jobs()