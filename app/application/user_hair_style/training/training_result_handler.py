# import json
# import logging
# from datetime import datetime, UTC, timedelta
# from typing import Tuple

# from app.application.generation.request.dto.generation_mq import ImageInfo
# from app.core.config import image_generation_settings
# from app.domain.training.services.thumbnail_generation import get_thumbnail_image_size
# from app.application.user_hair_style.thumbnail_generation.dto.thumbnail_mq import ThumbnailGenerationPublishMessage
# from app.domain.training.models.training import TrainingRequest
# from app.core.config import rabbit_mq_settings, base_settings
# from app.infrastructure.alert.discord_webhook import send_error_notification
# from app.core.constants import FCMConstants, TrainingMessageData
# from app.domain.training.schemas.training.training_job import TrainingJobUpdate
# from app.domain.user.models.user import User
# from app.domain.training.models.training import TrainingJob
# from app.infrastructure.repositories.user.user import UserRepository
# from app.infrastructure.fcm.fcm_service import FCMService
# from app.domain.training.enums.training_status import TrainingJobStatus
# from app.application.user_hair_style.training.dto.training_mq import TrainingConsumeMessage
# from app.infrastructure.database.transaction import transactional
# from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
# from app.infrastructure.database.unit_of_work import UnitOfWork 
# from app.application.transactional_service import TransactionalService
# from app.infrastructure.repositories.training.user_hair_style import UserHairStyleLoraRepository
# from app.domain.training.models.user_hair_style import UserHairStyleLora
# from app.domain.training.schemas.user_hair_style.user_hair_style_lora import UserHairStyleLoraCreate
# from app.infrastructure.repositories.training.training import TrainingJobRepository, TrainingRequestRepository
# from app.domain.training.schemas.training.training_request import TrainingRequestUpdate
# from app.domain.training.enums.training_status import TrainingRequestStatus
# from app.domain.generation.services.calculate_remaining_time import CalculateRemainingTimeService
# from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository
# from app.domain.training.models.user_hair_style import UserHairStyle
# from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleUpdate
# from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus

# logger = logging.getLogger(__name__)

# class TrainingResultHandler(TransactionalService):
#     def __init__(
#             self,
#             user_repo: UserRepository,
#             training_request_repo: TrainingRequestRepository,
#             training_job_repo: TrainingJobRepository,
#             user_hair_style_lora_repo: UserHairStyleLoraRepository,
#             user_hair_style_repo: UserHairStyleRepository,
#             calculate_remaining_time_service: CalculateRemainingTimeService,
#             rabbit_mq_service: RabbitMQService,
#             fcm_service: FCMService,
#             unit_of_work: UnitOfWork,
#     ):
#         super().__init__(unit_of_work)
#         self.user_repo = user_repo

#         self.training_request_repo = training_request_repo
#         self.training_job_repo = training_job_repo
#         self.user_hair_style_lora_repo = user_hair_style_lora_repo
#         self.user_hair_style_repo = user_hair_style_repo

#         self.calculate_remaining_time_service = calculate_remaining_time_service

#         self.rabbit_mq_service = rabbit_mq_service
#         self.fcm_service = fcm_service


#     async def _get_thumbnail_creation_duration(self) -> int:
#         _, generation_consumer_count = await self.rabbit_mq_service.get_queue_info(
#             queue_name=rabbit_mq_settings.RABBITMQ_INFERENCE_CONSUME,
#         )

#         _, upscale_consumer_count = await self.rabbit_mq_service.get_queue_info(
#             queue_name=rabbit_mq_settings.RABBITMQ_UPSCALE_CONSUME,
#         )

#         return self.calculate_remaining_time_service.get_generation_job_expire_time(
#             is_high_resolution=False,
#             generation_consumer_count=generation_consumer_count,
#             upscale_consumer_count=upscale_consumer_count,
#             image_count=1,
#         )


#     @transactional
#     async def _handle_success(self, message: TrainingConsumeMessage) -> Tuple[TrainingJob, UserHairStyleLora, UserHairStyle]:

#         thumbnail_creation_duration: int = await self._get_thumbnail_creation_duration()

#         training_job: TrainingJob = self.training_job_repo.update_with_flush(
#             obj_id=message.training_job_id,
#             obj_in=TrainingJobUpdate(
#                 status=TrainingJobStatus.THUMBNAIL_GENERATING,
#                 actual_training_time_sec=message.actual_training_time_sec,
#                 response_at=datetime.now(UTC),
#                 thumbnail_creation_expires_at=datetime.now(UTC) + timedelta(seconds=thumbnail_creation_duration),
#             )
#         )

#         training_request: TrainingRequest = self.training_request_repo.get_with_user(training_job.id)
#         user: User = training_request.user

#         user_hair_style_lora: UserHairStyleLora = self.user_hair_style_lora_repo.create_with_flush(
#             obj_in=UserHairStyleLoraCreate(
#                 training_request_id=training_job.training_request_id,
#                 user_id=user.id,
#                 lora_name=message.user_hair_lora_name,
#                 lora_s3_key=message.user_hair_lora_s3_key,
#             )
#         )
#         user_hair_style: UserHairStyle = self.user_hair_style_repo.get_by_training_request(training_job.training_request_id)

#         user_hair_style: UserHairStyle = self.user_hair_style_repo.update(
#             obj_id=user_hair_style.id,
#             obj_in=UserHairStyleUpdate(
#                 user_hair_style_lora_id=user_hair_style_lora.id,
#             )
#         )

#         return training_job, user_hair_style_lora, user_hair_style

#     @transactional
#     def _handle_failure(self, message: TrainingConsumeMessage) -> Tuple[TrainingJob, TrainingRequest, UserHairStyle]:
#         training_job: TrainingJob = self.training_job_repo.update_with_flush(
#             obj_id=message.training_job_id,
#             obj_in=TrainingJobUpdate(
#                 status=TrainingJobStatus.FAILED,
#                 actual_training_time_sec=message.actual_training_time_sec,
#                 response_at=datetime.now(),
#             )
#         )

#         training_request: TrainingRequest = self.training_request_repo.update_with_flush(
#             obj_id=training_job.training_request_id,
#             obj_in=TrainingRequestUpdate(
#                 status=TrainingRequestStatus.FAILED,
#             )
#         )

#         user_hair_style: UserHairStyle = self.user_hair_style_repo.get_by_training_request(training_job.training_request_id)

#         user_hair_style: UserHairStyle = self.user_hair_style_repo.update_with_flush(
#             obj_id=user_hair_style.id,
#             obj_in=UserHairStyleUpdate(
#                 status=UserHairStyleStatus.FAILED,
#             )
#         )

#         return training_job, training_request, user_hair_style

#     async def _handle_success_and_publish_mq(self, message: TrainingConsumeMessage):

#         # transaction
#         training_job, user_hair_lora, user_hair_style = await self._handle_success(message)

#         thumbnail_s3_key: str = training_job.thumbnail_s3_key

#         time_to_live_sec: int = int((training_job.thumbnail_creation_expires_at - datetime.now(UTC)).total_seconds())

#         # 썸네일 생성 작업 publish
#         await self.rabbit_mq_service.publish(
#             message=ThumbnailGenerationPublishMessage(
#                 training_job_id=training_job.id,
#                 image_count=1,
#                 image_info_list=[ImageInfo(s3_key=thumbnail_s3_key, generated_image_id=0)],
#                 time_to_live_sec=time_to_live_sec,
#                 is_user_hair_style=True,
#                 lora_model_s3_key=user_hair_lora.lora_s3_key,
#                 lora_model_name=user_hair_lora.lora_name,
#                 prompt=training_job.thumbnail_prompt,
#                 width=training_job.thumbnail_width,
#                 height=training_job.thumbnail_height,
#                 distilled_cfg_scale=image_generation_settings.DISTILLED_CFG_SCALE,
#                 is_user_reference_image=False,
#             ).model_dump_json(),
#             queue_name=rabbit_mq_settings.RABBITMQ_INFERENCE_PUBLISH,
#         )
    
#     def _handle_failure_and_notify_fcm(self, message: TrainingConsumeMessage):

#         # transaction
#         training_job, training_request, user_hair_style = self._handle_failure(message)

#         user: User = self.user_repo.get(training_request.user_id)

#         # 스타일 등록 실패 디스코드(for 개발) 및 fcm 알림(for 유저) 전송
#         send_error_notification(
#             webhook_url=base_settings.ALERT_DISCORD_WEBHOOK,
#             error=Exception(f"스타일 학습 실패: {training_job.id}"),
#         )

#         self.fcm_service.send_to_token(
#             token=user.fcm_token,
#             title=FCMConstants.USER_HAIRSTYLE_TRAINING_FAILURE_TITLE,
#             body=FCMConstants.USER_HAIRSTYLE_TRAINING_FAILURE_BODY,
#             data=TrainingMessageData(
#                 user_hair_style_id=user_hair_style.id,
#             ).model_dump_str(),
#         )

#     async def handle_training_result(self, body: bytes):
#         data_dict = json.loads(body)
#         message = TrainingConsumeMessage(**data_dict)

#         logger.info(f"[MQ] Consumed Trainig Job ID: {message.training_job_id}. DETAILS: {message.model_dump_json()}")

#         if message.is_success:
#             await self._handle_success_and_publish_mq(message)
#         else:
#             self._handle_failure_and_notify_fcm(message)



# from app.core.db.base import get_db
# from app.infrastructure.repositories.training.training import get_training_request_repository, get_training_job_repository
# from app.infrastructure.repositories.user.user import get_user_repository
# from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_lora_repository, UserHairStyleLoraRepository
# from app.infrastructure.fcm.fcm_service import get_fcm_service
# from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service_singleton
# from app.infrastructure.database.unit_of_work import get_unit_of_work
# from app.domain.generation.services.calculate_remaining_time import get_calculate_remaining_time_service
# from app.infrastructure.repositories.generation.generation import get_generation_job_repository
# from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository

# async def handle_training_result(body: bytes) -> None:
#     db = next(get_db())
#     try:
#         user_repository: UserRepository = get_user_repository(db)

#         training_request_repository: TrainingRequestRepository = get_training_request_repository(db)
#         training_job_repository: TrainingJobRepository = get_training_job_repository(db)
#         user_hair_style_lora_repository: UserHairStyleLoraRepository = get_user_hair_style_lora_repository(db)
#         user_hair_style_repository: UserHairStyleRepository = get_user_hair_style_repository(db)
#         calculate_remaining_time_service: CalculateRemainingTimeService = get_calculate_remaining_time_service(
#             generation_job_repo=get_generation_job_repository(db),
#         )

#         rabbit_mq_service: RabbitMQService = await get_rabbit_mq_service_singleton()
#         fcm_service: FCMService = get_fcm_service()
#         unit_of_work: UnitOfWork = get_unit_of_work(db)

#         message_handler = TrainingResultHandler(
#             user_repo=user_repository,
#             training_request_repo=training_request_repository,
#             training_job_repo=training_job_repository,
#             user_hair_style_lora_repo=user_hair_style_lora_repository,
#             user_hair_style_repo=user_hair_style_repository,
#             calculate_remaining_time_service=calculate_remaining_time_service,
#             rabbit_mq_service=rabbit_mq_service,
#             fcm_service=fcm_service,
#             unit_of_work=unit_of_work,
#         )

#         await message_handler.handle_training_result(body)
#     finally:
#         db.close()
