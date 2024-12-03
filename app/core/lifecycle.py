import asyncio
import logging
from typing import Optional

from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.task.retry import RetryTaskManager
from app.application.services.generation.handle import handle_message

logger = logging.getLogger(__name__)


class LifespanServices:
   def __init__(self):
       self.mq_service: Optional[RabbitMQService] = None
       self.retry_task: Optional[asyncio.Task] = None
       self.consume_task: Optional[asyncio.Task] = None

   async def initialize(self):
       """서비스들 초기화"""

       # RabbitMQ 서비스 초기화
       self.mq_service = RabbitMQService()
       await self.mq_service.connect()

       # 태스크 시작
       retry_manager = RetryTaskManager(
           rabbit_mq_service=self.mq_service,
           check_interval=60
       )

       consume_manager = ConsumeTaskManager(
           rabbit_mq_service=self.mq_service,
       )

       # 코루틴 태스크 시작
       self.retry_task = asyncio.create_task(retry_manager.start())
       self.consume_task = asyncio.create_task(consume_manager.start())


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


class ConsumeTaskManager:
   def __init__(self, rabbit_mq_service: RabbitMQService):
       self.rabbit_mq_service = rabbit_mq_service

   async def start(self):
       try:
           await self.rabbit_mq_service.consume(handle_message)
           while True:
               await asyncio.sleep(3600)
       except Exception as e:
           logger.error(f"Consume task encountered an error: {e}")
           await asyncio.sleep(5)
           await self.start()  # 재시작
