import asyncio
import logging
from typing import Optional, List

from app.core.config import rabbit_mq_settings
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService, get_rabbit_mq_service_singleton
from app.infrastructure.task.base import TaskManager
from app.infrastructure.task.task import FailedRequestTaskManager, TokenRefillTaskManager, ConsumeTaskManager

logger = logging.getLogger(__name__)

class LifespanServices:
    def __init__(self):
        self.mq_service: Optional[RabbitMQService] = None
        self.tasks: List[asyncio.Task] = []

    async def initialize(self):
        # 태스크가 의존하는 싱글톤 인스턴스들 초기화
        self.mq_service = await get_rabbit_mq_service_singleton()

        consume_task_managers: List[TaskManager] = [
            ConsumeTaskManager(
                rabbit_mq_service=self.mq_service,
                consume_queue=queue_name
            )
            for queue_name in [
                rabbit_mq_settings.RABBITMQ_TRAINING_CONSUME,
                rabbit_mq_settings.RABBITMQ_INFERENCE_CONSUME,
                rabbit_mq_settings.RABBITMQ_UPSCALE_CONSUME,
            ]
        ]

        task_managers: List[TaskManager] = [
            FailedRequestTaskManager(),
            TokenRefillTaskManager(),
            *consume_task_managers,
        ]

        # 모든 태스크 시작
        for manager in task_managers:
            self.tasks.append(asyncio.create_task(manager.start()))

    async def cleanup(self):
        """모든 리소스 정리"""
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        if self.mq_service:
            await self.mq_service.close()