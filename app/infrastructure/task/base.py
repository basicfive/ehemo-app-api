from abc import ABC, abstractmethod
import asyncio
from logging import getLogger
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import timezone_settings

logger = getLogger(__name__)


class TaskManager(ABC):
    """모든 태스크 매니저가 구현해야 하는 기본 인터페이스"""

    @abstractmethod
    async def start(self):
        """태스크 실행을 시작"""
        pass

    @abstractmethod
    async def stop(self):
        """태스크 실행을 중지"""
        pass

class AsyncTaskManager(TaskManager):
    """비동기 태스크 관리를 위한 기본 클래스"""

    def __init__(self, check_interval: int):
        self.check_interval = check_interval
        self.is_running = False

    @abstractmethod
    async def execute(self):
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


class DailyTaskManager(TaskManager):
    """매일 특정 시간에 실행되는 태스크를 위한 기본 클래스"""

    def __init__(self, target_hour: int, timezone: str = timezone_settings.SEOUL):
        self.target_hour = target_hour
        self.timezone = ZoneInfo(timezone)
        self.is_running = False

    @abstractmethod
    async def execute(self):
        pass

    def _get_next_run_time(self) -> datetime:
        """다음 실행 시간을 계산"""
        now = datetime.now(self.timezone)
        target_time = now.replace(hour=self.target_hour, minute=0, second=0, microsecond=0)

        if now >= target_time:
            # 이미 오늘의 타겟 시간이 지났으면, 다음날 타겟 시간으로 설정
            target_time += timedelta(days=1)

        return target_time

    async def start(self):
        if self.is_running:
            return

        self.is_running = True
        while self.is_running:
            try:
                # 다음 실행 시간까지 대기
                next_run = self._get_next_run_time()
                now = datetime.now(self.timezone)
                wait_seconds = (next_run - now).total_seconds()

                await asyncio.sleep(wait_seconds)

                # 실행
                await self.execute()

            except Exception as e:
                logger.error(f"Daily task execution error: {e}")
                # 에러 발생 시 1분 대기 후 재시도
                await asyncio.sleep(60)

    async def stop(self):
        self.is_running = False


class ContinuousTaskManager(TaskManager):
    """중단 없이 계속 실행되어야 하는 태스크를 위한 기본 클래스"""

    def __init__(self, retry_interval: int = 5):
        self.retry_interval = retry_interval
        self.is_running = False

    @abstractmethod
    async def execute_continuous(self):
        """지속적으로 실행되어야 하는 태스크 구현"""
        pass

    async def start(self):
        if self.is_running:
            return

        self.is_running = True
        while self.is_running:
            try:
                await self.execute_continuous()
            except Exception as e:
                logger.error(f"Continuous task execution error: {e}")
                await asyncio.sleep(self.retry_interval)

    async def stop(self):
        self.is_running = False