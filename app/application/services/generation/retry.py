import logging
from datetime import datetime, timedelta, UTC
from typing import List

from app.application.services.generation.dto.mq import MQPublishMessage
from app.core.enums.generation_status import GenerationStatusEnum, GenerationResultEnum
from app.core.enums.message_priority import MessagePriority
from app.core.errors.exceptions import NoInferenceConsumerException
from app.domain.generation.models.generation import ImageGenerationJob, GenerationRequest
from app.domain.generation.schemas.generation_request import GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobUpdate, ImageGenerationJobInDB
from app.domain.generation.services.generation_domain_service import estimate_normal_priority_message_wait_sec, \
    estimate_high_priority_message_wait_sec, calculate_retry_message_ttl_sec
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserUpdate
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.repositories.generation.generation import ImageGenerationJobRepository, \
    GenerationRequestRepository
from app.core.config import image_generation_setting
from app.infrastructure.repositories.user.user import UserRepository

logger = logging.getLogger()

class ImageGenerationRetryService:
    def __init__(
            self,
            image_generation_job_repo: ImageGenerationJobRepository,
            generation_request_repo: GenerationRequestRepository,
            user_repo: UserRepository,
            rabbit_mq_service: RabbitMQService,
            fcm_service: FCMService
    ):
        self.image_generation_job_repo = image_generation_job_repo
        self.generation_request_repo = generation_request_repo
        self.user_repo = user_repo
        self.rabbit_mq_service = rabbit_mq_service
        self.fcm_service = fcm_service

    async def retry_expired_jobs(self):
        expired_jobs: List[ImageGenerationJob] = self.image_generation_job_repo.get_all_expired_but_to_process_jobs()

        logger.info(f"Found {len(expired_jobs)} expired jobs to process...")
        if not expired_jobs:
            return

        message_count, consumer_count = await self.rabbit_mq_service.get_queue_info()
        if consumer_count < 1:
            raise NoInferenceConsumerException()

        current_message_expire_at = estimate_high_priority_message_wait_sec(
            image_count=message_count,
            processor_count=consumer_count
        )

        for expired_job in expired_jobs:
            # [FAILED 처리]
            if expired_job.retry_count >= image_generation_setting.MAX_RETRIES:
                self._check_request_failed_and_notify_fcm(expired_job)
                continue

            current_message_expire_at += calculate_retry_message_ttl_sec()

            # 재요청 - mq 높은 우선순위
            self.image_generation_job_repo.update(
                obj_id=expired_job.id,
                obj_in=ImageGenerationJobUpdate(
                    retry_count=expired_job.retry_count + 1,
                    expires_at=datetime.now(UTC) + timedelta(seconds=current_message_expire_at)
                )
            )
            image_generation_job = ImageGenerationJobInDB.model_validate(expired_job)
            message = MQPublishMessage(
                **image_generation_job.model_dump(),
                image_generation_job_id=expired_job.id,
            )

            await self.rabbit_mq_service.publish(
                message=message,
                expiration_sec=current_message_expire_at,
                priority=MessagePriority.URGENT
            )

    def _check_request_failed_and_notify_fcm(self, expired_job: ImageGenerationJob):
        self.image_generation_job_repo.update(
            obj_id=expired_job.id,
            obj_in=ImageGenerationJobUpdate(status=GenerationStatusEnum.FAILED)
        )
        logger.info(f"Job ID: {expired_job.id} has exhausted all retry attempts. Marked as failed.")

        # 아직 fcm 에러를 보내지 않았다면, fcm 전송 후 generation request 업데이트
        generation_request: GenerationRequest = self.generation_request_repo.get(expired_job.generation_request_id)
        if generation_request.generation_result == GenerationResultEnum.PENDING:
            # self.fcm_service.send_notification()

            # 유저 토큰 반환 - 이걸 잘 묶어줘야할듯.
            user: User = self.user_repo.get(generation_request.user_id)
            self.user_repo.update(obj_id=user.id, obj_in=UserUpdate(token=user.token + 1))

            self.generation_request_repo.update(
                obj_id=generation_request.id,
                obj_in=GenerationRequestUpdate(generation_result=GenerationResultEnum.FAILED)
            )
