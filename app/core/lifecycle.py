import asyncio
import logging
from typing import List

from app.infrastructure.task.base import TaskManager
from app.infrastructure.task.task import FailedRequestTaskManager, TokenRefillTaskManager

logger = logging.getLogger(__name__)

class LifespanServices:
    def __init__(self):
        self.tasks: List[asyncio.Task] = []

    async def initialize(self):

        task_managers: List[TaskManager] = [
            FailedRequestTaskManager(),
            TokenRefillTaskManager(),
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