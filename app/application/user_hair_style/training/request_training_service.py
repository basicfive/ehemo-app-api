from typing import List, Tuple
from datetime import datetime, UTC

from app.application.user_hair_style.training.dto.training_mq import TrainingPublishMessage
from app.core.config import training_settings, rabbit_mq_settings
from app.domain.user.models.user import User
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.core.errors.http_exceptions import ValueException
from app.application.user_hair_style.training.dto.request_training import UserHairStyleRegisterRequest, UserHairStyleRegisterResponse
from app.application.transactional_service import TransactionalService
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.domain.training.services.training_request_service import TrainingRequestService
from app.domain.training.services.user_hair_lora_naming import create_user_hair_lora_name, create_user_hair_lora_s3_key
from app.infrastructure.s3.s3_client import S3Client
from app.application.generation.request.dto.request import ImageUploadUrlDto
from app.domain.training.services.uploaded_image_for_training import create_uploaded_image_for_training_s3_key
from app.core.errors.exceptions import NoTrainingConsumerException
from app.domain.training.services.thumbnail_generation import ThumbnailPromptService
from app.infrastructure.google_genai.genai_api import async_gemini_translate_prompt

class RequestTrainingService(TransactionalService):
    def __init__(
            self,
            user_repository: UserRepository,
            training_request_service: TrainingRequestService,
            thumbnail_prompt_service: ThumbnailPromptService,
            rabbit_mq_service: RabbitMQService,
            unit_of_work: UnitOfWork,
            s3_client: S3Client,
        ):
        super().__init__(unit_of_work)
        self.user_repository = user_repository
        self.training_request_service = training_request_service
        self.thumbnail_prompt_service = thumbnail_prompt_service
        self.rabbit_mq_service = rabbit_mq_service
        self.s3_client = s3_client

    def get_upload_urls_for_training_images(self, image_cnt: int) -> List[ImageUploadUrlDto]:
        upload_urls: List[ImageUploadUrlDto] = []

        for _ in range(image_cnt):
            s3_key = create_uploaded_image_for_training_s3_key()
            upload_url = self.s3_client.create_put_presigned_url(s3_key=s3_key)
            upload_urls.append(
                ImageUploadUrlDto(
                    upload_url=upload_url,
                    s3_key=s3_key,
                )
            )
        return upload_urls
    

    async def request_training(self, request: UserHairStyleRegisterRequest, user_id: int) -> UserHairStyleRegisterResponse:
        message, response = await self._request_training(request, user_id)
        await self.rabbit_mq_service.publish(
            message=message.model_dump_json(),
            queue_name=rabbit_mq_settings.RABBITMQ_TRAINING_PUBLISH,
        )
        return response

    @transactional
    async def _request_training(self, request: UserHairStyleRegisterRequest, user_id: int) -> Tuple[TrainingPublishMessage, UserHairStyleRegisterResponse]:
        # 1. 업로드 된 이미지 갯수 validation (서버 쪽에서 한 번 더)
        if len(request.uploaded_image_s3_keys) < training_settings.MINIMUM_IMAGE_CNT_FOR_TRAINING:
            raise ValueException(f"이미지는 최소 {training_settings.MINIMUM_IMAGE_CNT_FOR_TRAINING}개 이상이어야해요")
        if len(request.uploaded_image_s3_keys) > training_settings.MAXIMUM_IMAGE_CNT_FOR_TRAINING:
            raise ValueException(f"이미지 최대 갯수 {training_settings.MAXIMUM_IMAGE_CNT_FOR_TRAINING}를 초과했어요")
        
        # 2. 현재 학습 서버 연결 여부 확인
        _, consumer_count = await self.rabbit_mq_service.get_queue_info(queue_name=rabbit_mq_settings.RABBITMQ_TRAINING_PUBLISH)
        if consumer_count < 1:
            raise NoTrainingConsumerException()

        # 3. 사용자 존재 여부 확인
        try:
            user: User = self.user_repository.get(user_id)
        except Exception:
            raise ValueException("사용자를 찾을 수 없습니다.")

        # 4. 현재 진행 중인 training 있는지 확인
        if self.training_request_service.is_user_training_request_pending(user.id):
            raise ValueException("현재 등록 중인 헤어스타일이 있어요. 등록이 완료된 후 새로운 스타일을 등록해주세요")

        # 5. 썸네일 프롬프트 생성
        korean_thumbnail_prompt: str = self.thumbnail_prompt_service.create_thumbnail_prompt(gender=request.gender)
        english_thumbnail_prompt: str = await async_gemini_translate_prompt(korean_thumbnail_prompt)

        training_request, images_for_training, training_job, user_hair_style = self.training_request_service.create_training_request_and_job(
            gender=request.gender,
            user=user,
            title=request.title,
            description=request.description,
            uploaded_images_s3_keys=request.uploaded_image_s3_keys,
            thumbnail_prompt=english_thumbnail_prompt,
        )

        user_hair_lora_name: str = create_user_hair_lora_name()
        user_hair_lora_s3_key: str = create_user_hair_lora_s3_key(user_hair_lora_name)

        training_message = TrainingPublishMessage(
            gender=training_job.gender,
            training_job_id=training_job.id,
            user_hair_lora_s3_key=user_hair_lora_s3_key,
            user_hair_lora_name=user_hair_lora_name,
            uploaded_image_s3_keys=[image_for_training.s3_key for image_for_training in images_for_training],
            total_steps=training_job.total_steps,
            epoch=training_job.epoch,
        )

        estimated_time_sec: int = int((training_job.expires_at - datetime.now(UTC)).total_seconds())
        response = UserHairStyleRegisterResponse(
            estimated_time_sec=estimated_time_sec,
        )
        return training_message, response


from fastapi import Depends
from app.infrastructure.repositories.user.user import get_user_repository
from app.domain.training.services.training_request_service import get_training_request_service
from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.s3.s3_client import get_s3_client
from app.domain.training.services.thumbnail_generation import get_thumbnail_prompt_service

def get_request_training_service(
        user_repository: UserRepository = Depends(get_user_repository),
        training_request_service: TrainingRequestService = Depends(get_training_request_service),
        thumbnail_prompt_service: ThumbnailPromptService = Depends(get_thumbnail_prompt_service),
        rabbit_mq_service: RabbitMQService = Depends(get_rabbit_mq_service),
        s3_client: S3Client = Depends(get_s3_client),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> RequestTrainingService:
    return RequestTrainingService(
        user_repository=user_repository,
        training_request_service=training_request_service,
        thumbnail_prompt_service=thumbnail_prompt_service,
        rabbit_mq_service=rabbit_mq_service,
        s3_client=s3_client,
        unit_of_work=unit_of_work,
    )