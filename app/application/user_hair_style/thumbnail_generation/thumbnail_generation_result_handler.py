import json
import logging
from datetime import datetime, UTC
from typing import Tuple, List

from app.core.config import rabbit_mq_settings
from app.domain.training.models.training import TrainingJob
from app.domain.user.models.user import User
from app.application.transactional_service import TransactionalService
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.repositories.user.user import UserRepository
from app.domain.training.services.training_request_service import TrainingRequestService
from app.infrastructure.repositories.training.training import TrainingRequestRepository
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.s3.s3_client import S3Client
from app.application.user_hair_style.thumbnail_generation.dto.thumbnail_mq import ThumbnailGenerationConsumeMessage, ThumbnailUpscalePublishMessage
from app.domain.training.schemas.training.training_job import TrainingJobUpdate
from app.infrastructure.repositories.training.training import TrainingJobRepository
from app.domain.training.enums.training_status import TrainingJobStatus
from app.application.generation.request.dto.upscale_mq import UpscaleImageInfo

logger = logging.getLogger(__name__)

class ThumbnailGenerationResultHandler(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            training_request_repo: TrainingRequestRepository,
            training_job_repo: TrainingJobRepository,
            rabbit_mq_service: RabbitMQService,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.training_request_repo = training_request_repo
        self.training_job_repo = training_job_repo
        self.rabbit_mq_service = rabbit_mq_service
        self.s3_client = s3_client
    
    @transactional
    def mark_after_generation_success(self, training_job_id: int) -> TrainingJob:
        return self.training_job_repo.update_with_flush(
            obj_id=training_job_id,
            obj_in=TrainingJobUpdate(
                status=TrainingJobStatus.THUMBNAIL_UPSCALING,
            )
        )

    @transactional
    def mark_after_generation_failure(self, training_job_id: int) -> None:
        # 썸네일 제작으로 인한 실패는 썸네일 제작 실패 카운트만 증가시키고 끝내면 됨. (헤어스타일 / request 에 대한 실패처리는 재시도 로직에서 다룰 것)
        training_job: TrainingJob = self.training_job_repo.get(training_job_id)
        self.training_job_repo.update_with_flush(
            obj_id=training_job.id,
            obj_in=TrainingJobUpdate(
                thumbnail_creation_failure_count=training_job.thumbnail_creation_failure_count + 1,
            )
        )
    
    async def _handle_success(self, message: ThumbnailGenerationConsumeMessage) -> None:
        # transaction
        training_job: TrainingJob = self.mark_after_generation_success(message.training_job_id)

        image_info_list = []
        for message_image_info in message.image_info_list:
            image_info_list.append(
                UpscaleImageInfo(
                    generated_image_id=message.training_job_id,
                    s3_key=message_image_info.s3_key,
                    upscale_s3_key=message_image_info.s3_key,
                )
            )

        time_to_live_sec = int((training_job.thumbnail_creation_expires_at - datetime.now(UTC)).total_seconds())

        await self.rabbit_mq_service.publish(
            message=ThumbnailUpscalePublishMessage(
                training_job_id=message.training_job_id,
                image_info_list=image_info_list,
                time_to_live_sec=time_to_live_sec,
                prompt=message.prompt,
                width=message.width,
                height=message.height,
            ).model_dump_json(),
            queue_name=rabbit_mq_settings.RABBITMQ_UPSCALE_PUBLISH,
        )

    def _handle_failure(self, message: ThumbnailGenerationConsumeMessage) -> None:
        # transaction
        self.mark_after_generation_failure(message.training_job_id)


    async def handle_thumbnail_generation_result(self, body: bytes) -> None:
        data_dict = json.loads(body)
        message = ThumbnailGenerationConsumeMessage(**data_dict)
        logger.info(f"[MQ] Consumed Job ID: {message.training_job_id}. DETAILS: {message.model_dump_json()}")

        if message.is_success:
            await self._handle_success(message)
        else:
            self._handle_failure(message)


from app.core.db.base import get_db
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service_singleton
from app.infrastructure.repositories.training.training import get_training_job_repository, get_training_request_repository
from app.infrastructure.s3.s3_client import get_s3_client

async def handle_thumbnail_generation_result(body: bytes) -> None:
    db = next(get_db())
    try:
        training_request_repository: TrainingRequestRepository = get_training_request_repository(db)
        training_job_repository: TrainingJobRepository = get_training_job_repository(db)

        rabbit_mq_service: RabbitMQService = await get_rabbit_mq_service_singleton()
        s3_client: S3Client = get_s3_client()
        unit_of_work: UnitOfWork = get_unit_of_work(db)

        message_handler = ThumbnailGenerationResultHandler(
            training_request_repo=training_request_repository,
            training_job_repo=training_job_repository,
            rabbit_mq_service=rabbit_mq_service,
            s3_client=s3_client,
            unit_of_work=unit_of_work,
        )

        await message_handler.handle_thumbnail_generation_result(body)
    finally:
        db.close()