from app.application.services.generation.retry import ImageGenerationRetryService
from app.domain.generation.models.generation import ImageGenerationJob
from app.infrastructure.task.base import AsyncTaskManager


class RetryTaskManager(AsyncTaskManager):
    def __init__(
            self,
            retry_service: ImageGenerationRetryService,
            session_factory,
            check_interval: int = 60
    ):
        super().__init__(check_interval)
        self.retry_service = retry_service
        self.session_factory = session_factory

    async def execute(self):
        # 동기식 세션이므로 'with' 구문을 사용합니다.
        with self.session_factory() as session:
            # 새로운 세션으로 repository 재생성
            self.retry_service.image_generation_job_repo = self.retry_service.image_generation_job_repo.__class__(
                db=session
            )
            self.retry_service.generation_request_repo = self.retry_service.generation_request_repo.__class__(
                db=session
            )
            self.retry_service.user_repo = self.retry_service.user_repo.__class__(
                db=session
            )

            # retry_expired_jobs() 메서드가 비동기 함수이므로 'await'을 사용합니다.
            await self.retry_service.retry_expired_jobs()

            # 세션을 명시적으로 커밋하여 트랜잭션을 종료합니다.
            session.commit()