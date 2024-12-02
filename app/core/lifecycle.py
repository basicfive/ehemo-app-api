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
       self._session_factory = SessionLocal
       self.container = DependencyContainer(self._session_factory)
       self.mq_service: Optional[RabbitMQService] = None
       self.retry_service: Optional[ImageGenerationRetryService] = None
       self.retry_task: Optional[asyncio.Task] = None
       self.consume_task: Optional[asyncio.Task] = None
       self.message_handler: Optional[MessageHandler] = None

   def get_session(self):
       return self._session_factory()

   async def initialize(self):
       """서비스들 초기화"""
       # MessageHandler 초기화
       self.message_handler = MessageHandler(self.container)

       # RabbitMQ 서비스 초기화
       self.mq_service = RabbitMQService()
       await self.mq_service.connect()

       # Retry 서비스 초기화
       with self.get_session() as session:
           self.retry_service = ImageGenerationRetryService(
               image_generation_job_repo=self.container.get_repository_with_session(ImageGenerationJobRepository, session),
               generation_request_repo=self.container.get_repository_with_session(GenerationRequestRepository, session),
               user_repo=self.container.get_repository_with_session(UserRepository, session),
               rabbit_mq_service=self.mq_service,
               fcm_service=self.container.fcm_service
           )

       # 태스크 시작
       retry_manager = RetryTaskManager(
           retry_service=self.retry_service,
           session_factory=self._session_factory,
           check_interval=60
       )

       # 코루틴 태스크 시작
       self.retry_task = asyncio.create_task(retry_manager.start())
       self.consume_task = asyncio.create_task(self._start_consuming())

   async def _start_consuming(self):
       retry_count = 0
       max_retries = 3
       while retry_count < max_retries:
           try:
               if self.mq_service and not await self.mq_service.check_connection():
                   await self.mq_service.ensure_connection()
               await self.mq_service.consume(self.message_handler.handle_message)
               retry_count = 0  # 성공시 카운트 리셋
               while True:
                   await asyncio.sleep(3600)
           except Exception as e:
               retry_count += 1
               logger.error(f"Consume error (attempt {retry_count}/{max_retries}): {e}")
               await asyncio.sleep(5 * retry_count)  # 점진적 대기

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