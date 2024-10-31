import asyncio
from typing import Optional

from app.application.services.generation.retry import ImageGenerationRetryService
from app.core.db.base import SessionLocal
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.repositories.generation.generation import ImageGenerationJobRepository, \
    GenerationRequestRepository
from app.infrastructure.repositories.user.user import UserRepository

from app.infrastructure.task.retry import RetryTaskManager


class LifespanServices:
    def __init__(self):
        self.db = SessionLocal()
        self.mq_service: Optional[RabbitMQService] = None
        self.retry_service: Optional[ImageGenerationRetryService] = None
        self.retry_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """서비스들 초기화"""
        # 동기 세션 생성

        # Repository 및 서비스 초기화
        image_generation_job_repository = ImageGenerationJobRepository(db=self.db)
        generation_request_repo = GenerationRequestRepository(db=self.db)
        user_repo = UserRepository(db=self.db)

        self.mq_service = RabbitMQService()
        await self.mq_service.connect()

        fcm_service = FCMService()  # FCM 서비스 초기화

        self.retry_service = ImageGenerationRetryService(
            image_generation_job_repo=image_generation_job_repository,
            generation_request_repo=generation_request_repo,
            user_repo=user_repo,
            rabbit_mq_service=self.mq_service,
            fcm_service=fcm_service
        )

        retry_manager = RetryTaskManager(
            retry_service=self.retry_service,
            check_interval=60
        )

        self.retry_task = asyncio.create_task(retry_manager.start())

    async def cleanup(self):
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass

        if self.mq_service:
            await self.mq_service.close()

        if self.db:
            self.db.close()
