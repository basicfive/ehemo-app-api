import json
import logging
from datetime import datetime

from app.core.config import image_generation_settings
from app.domain.training.services.thumbnail_generation import create_thumbnail_prompt, get_thumbnail_image_size
from app.core.enums.inference_types import InferenceType
from app.domain.training.services.user_hair_lora_naming import create_user_hair_style_thumbnail_s3_key
from app.application.user_hair_style.thumbnail_generation.dto.thumbnail_mq import ThumbnailGenerationPublishMessage
from app.domain.training.models.training import TrainingRequest
from app.core.config import rabbit_mq_settings
from app.infrastructure.alert.discord_webhook import send_error_notification
from app.core.constants import FCMConstants
from app.domain.training.schemas.training.training_job import TrainingJobUpdate
from app.domain.user.models.user import User
from app.domain.training.models.training import TrainingJob
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.fcm.fcm_service import FCMService
from app.domain.common.enums.ai_status import TrainingJobStatus
from app.domain.training.services.training_request_service import TrainingRequestService
from app.application.user_hair_style.training.dto.training_mq import TrainingConsumeMessage
from app.infrastructure.database.transaction import transactional
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.database.unit_of_work import UnitOfWork 
from app.application.transactional_service import TransactionalService
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleLoraRepository
from app.domain.training.models.user_hair_style import UserHairStyleLora
from app.domain.training.schemas.user_hair_style.user_hair_style_lora import UserHairStyleLoraCreate
from app.infrastructure.repositories.training.training import TrainingJobRepository, TrainingRequestRepository

logger = logging.getLogger(__name__)

class TrainingResultHandler(TransactionalService):
    def __init__(
            self,
            user_repository: UserRepository,
            user_hair_style_lora_repository: UserHairStyleLoraRepository,
            training_request_service: TrainingRequestService,
            training_job_repository: TrainingJobRepository,
            fcm_service: FCMService,
            rabbit_mq_service: RabbitMQService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repository = user_repository
        self.training_request_service = training_request_service
        self.training_job_repository = training_job_repository
        self.user_hair_style_lora_repository = user_hair_style_lora_repository
        self.rabbit_mq_service = rabbit_mq_service
        self.fcm_service = fcm_service

    def _update_training_job(self, training_job_id: int, actual_training_time_sec: int, status: TrainingJobStatus) -> TrainingJob:
        return self.training_job_repository.update_with_flush(
            obj_id=training_job_id,
            obj_in=TrainingJobUpdate(
                status=status,
                actual_training_time_sec=actual_training_time_sec,
                response_at=datetime.now(),
            )
        )

    @transactional
    def _handle_success_training_job(self, message: TrainingConsumeMessage, user: User) -> UserHairStyleLora:
        training_job: TrainingJob = self._update_training_job(message.training_job_id, message.actual_training_time_sec, TrainingJobStatus.COMPLETED)
        return self.user_hair_style_lora_repository.create_with_flush(
            obj_in=UserHairStyleLoraCreate(
                training_request_id=training_job.training_request_id,
                user_id=user.id,
                lora_name=message.user_hair_lora_name,
                lora_s3_key=message.user_hair_lora_s3_key,
            )
        )

    @transactional
    def _handle_failure_training_job(self, message: TrainingConsumeMessage, user: User):
        self._update_training_job(message.training_job_id, message.actual_training_time_sec, TrainingJobStatus.FAILED)


    async def handle_training_result(self, body: bytes):
        data_dict = json.loads(body)
        message = TrainingConsumeMessage(**data_dict)

        logger.info(f"[MQ] Consumed Trainig Job ID: {message.training_job_id}. DETAILS: {message.model_dump_json()}")

        training_request: TrainingRequest = self.training_request_service.get_training_request_with_user_by_training_job(message.training_job_id)
        user: User = training_request.user

        if message.is_success:
            user_hair_lora: UserHairStyleLora = self._handle_success_training_job(message, user)
            thumbnail_s3_key: str = create_user_hair_style_thumbnail_s3_key()
            width, height = get_thumbnail_image_size()
            await self.rabbit_mq_service.publish(
                message=ThumbnailGenerationPublishMessage(
                    inference_type=InferenceType.THUMBNAIL,
                    training_request_id=training_request.id,
                    user_hair_lora_s3_key=user_hair_lora.lora_s3_key,
                    user_hair_lora_name=user_hair_lora.lora_name,
                    thumbnail_s3_key=thumbnail_s3_key,
                    prompt=create_thumbnail_prompt(training_request.gender),
                    width=width,
                    height=height,
                    distilled_cfg_scale=image_generation_settings.DISTILLED_CFG_SCALE,
                ).model_dump_json(),
                queue_name=rabbit_mq_settings.RABBITMQ_EVENT_BUS,
            )

        else:
            self._handle_failure_training_job(message, user)

            # 스타일 등록 실패 디스코드(for 개발) 및 fcm 알림(for 유저) 전송
            send_error_notification(f"스타일 학습 실패: {message.training_job_id}")
            self.fcm_service.send_to_token(
                token=user.fcm_token,
                title=FCMConstants.USER_HAIRSTYLE_TRAINING_FAILURE_TITLE,
                body=FCMConstants.USER_HAIRSTYLE_TRAINING_FAILURE_BODY,
            )


from app.core.db.base import get_db
from app.domain.training.services.training_request_service import get_training_request_service
from app.infrastructure.repositories.training.training import get_training_request_repository, get_training_job_repository
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.s3.s3_client import get_s3_client
from app.infrastructure.alert.discord_webhook import send_error_notification
from app.infrastructure.repositories.training.image import get_training_request_uploaded_images_repository, get_uploaded_images_for_training_repository, TrainingRequestUploadedImagesRepository, UploadedImagesForTrainingRepository
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_lora_repository, UserHairStyleLoraRepository
from app.infrastructure.fcm.fcm_service import get_fcm_service
from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service_singleton
from app.infrastructure.database.unit_of_work import get_unit_of_work

async def handle_training_result(body: bytes) -> None:
    db = next(get_db())
    try:
        training_request_repository: TrainingRequestRepository = get_training_request_repository(db)
        training_job_repository: TrainingJobRepository = get_training_job_repository(db)
        training_request_uploaded_images_repository: TrainingRequestUploadedImagesRepository = get_training_request_uploaded_images_repository(db)
        uploaded_images_for_training_repository: UploadedImagesForTrainingRepository = get_uploaded_images_for_training_repository(db)

        user_repository: UserRepository = get_user_repository(db)
        user_hair_style_lora_repository: UserHairStyleLoraRepository = get_user_hair_style_lora_repository(db)
        fcm_service: FCMService = get_fcm_service(db)
        rabbit_mq_service: RabbitMQService = await get_rabbit_mq_service_singleton()
        unit_of_work: UnitOfWork = get_unit_of_work()

        training_request_service: TrainingRequestService = get_training_request_service(
            training_request_repository=training_request_repository,
            training_job_repository=training_job_repository,
            training_request_uploaded_images_repository=training_request_uploaded_images_repository,
            uploaded_images_for_training_repository=uploaded_images_for_training_repository,
        )

        message_handler = TrainingResultHandler(
            user_repository=user_repository,
            user_hair_style_lora_repository=user_hair_style_lora_repository,
            training_request_service=training_request_service,
            training_job_repository=training_job_repository,
            fcm_service=fcm_service,
            rabbit_mq_service=rabbit_mq_service,
            unit_of_work=unit_of_work,
        )

        # 비동기 처리 어케해야함?
        await message_handler.handle_training_result(body)
    finally:
        db.close()
