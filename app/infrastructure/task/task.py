from logging import getLogger

from app.application.services.generation.handle import handle_message
from app.application.services.generation.retry import retry_expired_jobs
from app.application.services.token.token_refill import refill_user_tokens
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.task.base import AsyncTaskManager, DailyTaskManager, ContinuousTaskManager

logger = getLogger(__name__)

class JobRetryTaskManager(AsyncTaskManager):
    def __init__(
            self,
            rabbit_mq_service: RabbitMQService,
            check_interval: int = 60
    ):
        super().__init__(check_interval)
        self.rabbit_mq_service = rabbit_mq_service

    async def execute(self):
        await retry_expired_jobs(rabbit_mq_service=self.rabbit_mq_service)

class ConsumeTaskManager(ContinuousTaskManager):
    """메시지 소비를 관리하는 태스크 매니저"""

    def __init__(
            self,
            rabbit_mq_service: RabbitMQService,
            retry_interval: int = 5,
    ):
        super().__init__(retry_interval)
        self.rabbit_mq_service = rabbit_mq_service

    async def execute_continuous(self):
        await self.rabbit_mq_service.consume(handle_message)

class TokenRefillTaskManager(DailyTaskManager):
    """토큰 리필을 관리하는 태스크 매니저 (매일 KST 자정에 실행)"""

    def __init__(self):
        super().__init__(target_hour=0)

    async def execute(self):
        refill_user_tokens()
