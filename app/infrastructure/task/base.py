from abc import ABC, abstractmethod
import asyncio
from logging import getLogger

logger = getLogger(__name__)

class AsyncTaskManager(ABC):
    """비동기 태스크 관리를 위한 기본 클래스"""

    def __init__(self, check_interval: int):
        self.check_interval = check_interval
        self.is_running = False

    @abstractmethod
    async def execute(self):
        """실행할 태스크 로직"""
        pass

    async def start(self):
        if self.is_running:
            return

        self.is_running = True
        while self.is_running:
            try:
                await self.execute()
            except Exception as e:
                logger.error(f"Task execution error: {e}")
            finally:
                await asyncio.sleep(self.check_interval)

    async def stop(self):
        self.is_running = False