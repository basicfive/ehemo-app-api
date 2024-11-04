import asyncio
import logging
from typing import Optional

from app.core.container import DependencyContainer
from app.core.db.base import SessionLocal
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.repositories.generation.generation import ImageGenerationJobRepository, \
    GenerationRequestRepository
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.task.retry import RetryTaskManager
from app.application.services.generation.handle import MessageHandler
from app.application.services.generation.retry import ImageGenerationRetryService

logger = logging.getLogger(__name__)


class LifespanServices:
    def __init__(self):
        self.db = SessionLocal()
        self.container = DependencyContainer(self.db)
        self.mq_service: Optional[RabbitMQService] = None
        self.retry_service: Optional[ImageGenerationRetryService] = None
        self.retry_task: Optional[asyncio.Task] = None
        self.consume_task: Optional[asyncio.Task] = None
        self.message_handler: Optional[MessageHandler] = None

    async def initialize(self):
        """서비스들 초기화"""
        # MessageHandler 초기화
        self.message_handler = MessageHandler(self.container)

        # RabbitMQ 서비스 초기화
        self.mq_service = RabbitMQService()
        await self.mq_service.connect()

        # Retry 서비스 초기화
        self.retry_service = ImageGenerationRetryService(
            image_generation_job_repo=self.container.get_repository(ImageGenerationJobRepository),
            generation_request_repo=self.container.get_repository(GenerationRequestRepository),
            user_repo=self.container.get_repository(UserRepository),
            rabbit_mq_service=self.mq_service,
            fcm_service=self.container.fcm_service
        )

        # 태스크 시작
        retry_manager = RetryTaskManager(
            retry_service=self.retry_service,
            check_interval=60
        )

        # 코루틴 태스크 시작
        self.retry_task = asyncio.create_task(retry_manager.start())
        self.consume_task = asyncio.create_task(self._start_consuming())

    async def _start_consuming(self):
        """RabbitMQ consume 작업을 시작하는 코루틴"""
        try:
            await self.mq_service.consume(self.message_handler.handle_message)
            # consume이 시작된 후 계속 실행 상태를 유지하기 위한 무한 대기
            while True:
                await asyncio.sleep(3600)  # 1시간마다 한번씩 체크
        except Exception as e:
            logger.error(f"Consume task encountered an error: {e}")
            # 에러 발생시 재시작
            await asyncio.sleep(5)  # 5초 대기 후 재시작
            self.consume_task = asyncio.create_task(self._start_consuming())

    async def cleanup(self):
        """모든 리소스 정리"""
        # 실행 중인 태스크들 정리
        tasks_to_cancel = [t for t in [self.retry_task, self.consume_task] if t]

        for task in tasks_to_cancel:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # 서비스 정리
        if self.mq_service:
            await self.mq_service.close()

        # 컨테이너를 통한 리소스 정리
        self.container.cleanup()