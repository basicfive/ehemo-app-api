from logging import getLogger
from typing import Callable
# from app.presentation.messaging.queue_router import QueueRouter

from app.application.generation.request.process_failed_request_service import process_failed_requests
from app.application.token.token_refill import refill_user_tokens
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.task.base import AsyncTaskManager, DailyTaskManager, ContinuousTaskManager

logger = getLogger(__name__)

class FailedRequestTaskManager(AsyncTaskManager):
    def __init__(
            self,
            check_interval: int = 60
    ):
        super().__init__(check_interval)

    async def execute(self):
        process_failed_requests()

# class ConsumeTaskManager(ContinuousTaskManager):
#     """메시지 소비를 관리하는 태스크 매니저"""

#     def __init__(
#             self,
#             rabbit_mq_service: RabbitMQService,
#             consume_queue: str,
#             retry_interval: int = 5,
#     ):
#         super().__init__(retry_interval)
#         self.rabbit_mq_service = rabbit_mq_service
#         self.consume_queue = consume_queue

#     async def execute_continuous(self):
#         try:
#             # 메시지 콜백을 전달
#             await self.rabbit_mq_service.consume(
#                 queue_name=self.consume_queue,
#                 callback=self._message_callback,
#             )
#         except Exception as e:
#             logger.error(f"RabbitMQ consume error in queue {self.consume_queue}: {e}")
#             raise e
    
#     async def _message_callback(self, body: bytes) -> None:
#         try:
#             # 큐에 맞는 핸들러 가져오기
#             handler = QueueRouter.get_handler(self.consume_queue)
            
#             # 메시지 내용에 따라 적절한 처리 함수 가져오기
#             processor = handler.handle(body)
            
#             # 처리 함수 실행 (동기/비동기 구분)
#             import inspect
#             if inspect.iscoroutinefunction(processor):
#                 await processor(body)
#             else:
#                 processor(body)
#         except Exception as e:
#             logger.error(f"Error processing message from {self.consume_queue}: {e}", exc_info=True)

class TokenRefillTaskManager(DailyTaskManager):
    """토큰 리필을 관리하는 태스크 매니저 (매일 KST 자정에 실행)"""

    def __init__(self):
        super().__init__(target_hour=0)

    async def execute(self):
        refill_user_tokens()
