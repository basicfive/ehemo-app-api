import asyncio
import logging
from typing import Optional

from app.application.services.generation.manage import handle_message
from app.application.services.generation.retry import ImageGenerationRetryService
from app.core.db.base import SessionLocal
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.repositories.generation.generation import ImageGenerationJobRepository, \
    GenerationRequestRepository
from app.infrastructure.repositories.user.user import UserRepository

from app.infrastructure.task.retry import RetryTaskManager

logger = logging.getLogger()

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

        self.consume_task = asyncio.create_task(self._start_consuming())

    async def _start_consuming(self):
        """RabbitMQ consume 작업을 시작하는 코루틴"""
        try:
            await self.mq_service.consume(handle_message)
            # consume이 시작된 후 계속 실행 상태를 유지하기 위한 무한 대기
            while True:
                await asyncio.sleep(3600)  # 1시간마다 한번씩 체크
        except Exception as e:
            logger.error(f"Consume task encountered an error: {e}")
            # 에러 발생시 재시작
            await asyncio.sleep(5)  # 5초 대기 후 재시작
            self.consume_task = asyncio.create_task(self._start_consuming())

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
