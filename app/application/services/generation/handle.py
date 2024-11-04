import json
import logging
from typing import List

from app.application.query.hair_model_query import HairModelQueryService
from app.application.services.generation.dto.mq import MQConsumeMessage
from app.core.config import aws_s3_setting
from app.core.container import DependencyContainer
from app.core.enums.generation_status import GenerationStatusEnum, NotificationStatus
from app.core.utils import generate_unique_datatime_uuid_key, concatenate_images_horizontally, compress_and_resize_image
from app.domain.generation.models.generation import ImageGenerationJob
from app.domain.generation.models.image import GeneratedImage
from app.domain.generation.schemas.generated_image import GeneratedImageCreate
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupCreate
from app.domain.generation.schemas.generation_request import GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobUpdate
from app.domain.generation.services.generation_domain_service import are_all_image_generation_jobs_complete
from app.infrastructure.repositories.generation.generation import (
    GenerationRequestRepository,
    ImageGenerationJobRepository,
    GeneratedImageRepository,
    GeneratedImageGroupRepository
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """메시지 처리를 위한 핸들러"""

    def __init__(self, container: DependencyContainer):
        self.container = container

    @property
    def generation_request_repo(self) -> GenerationRequestRepository:
        return self.container.get_repository(GenerationRequestRepository)

    @property
    def image_generation_job_repo(self) -> ImageGenerationJobRepository:
        return self.container.get_repository(ImageGenerationJobRepository)

    @property
    def generated_image_repo(self) -> GeneratedImageRepository:
        return self.container.get_repository(GeneratedImageRepository)

    @property
    def generated_image_group_repo(self) -> GeneratedImageGroupRepository:
        return self.container.get_repository(GeneratedImageGroupRepository)

    @property
    def hair_model_query_service(self) -> HairModelQueryService:
        return self.container.hair_model_query_service

    def handle_message(self, body: bytes) -> None:
        """메시지 처리의 메인 엔트리포인트"""
        try:
            data_dict = json.loads(body)
            message = MQConsumeMessage(**data_dict)

            logger.info(f"[MQ] Consumed Job ID: {message.image_generation_job_id}. DETAILS: {message.to_str()}")

            image_generation_job = self._process_generation_job(message)

            if self._should_create_image_group(image_generation_job):
                self._create_and_notify_image_group(image_generation_job)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise

    def _process_generation_job(self, message: MQConsumeMessage) -> ImageGenerationJob:
        """이미지 생성 작업 처리"""
        image_generation_job = self.image_generation_job_repo.get(message.image_generation_job_id)

        self.image_generation_job_repo.update(
            obj_id=image_generation_job.id,
            obj_in=ImageGenerationJobUpdate(
                webui_png_info=message.webui_png_info,
                status=GenerationStatusEnum.COMPLETED
            )
        )

        return image_generation_job

    def _should_create_image_group(self, job: ImageGenerationJob) -> bool:
        """이미지 그룹 생성 조건 확인"""
        image_generation_jobs = self.image_generation_job_repo.get_all_by_generation_request(
            generation_request_id=job.generation_request_id
        )
        return are_all_image_generation_jobs_complete(image_generation_jobs)

    def _create_and_notify_image_group(self, job: ImageGenerationJob) -> None:
        """이미지 그룹 생성 및 알림 처리"""
        image_generation_jobs = self.image_generation_job_repo.get_all_by_generation_request(
            generation_request_id=job.generation_request_id
        )

        # 이미지 그룹 생성
        generated_images = self._create_generated_images(
            image_generation_jobs,
            job.generation_request_id
        )

        # 알림 상태 업데이트
        generation_request = self.generation_request_repo.get(job.generation_request_id)
        self.generation_request_repo.update(
            obj_id=generation_request.id,
            obj_in=GenerationRequestUpdate(
                notification_status=NotificationStatus.SUCCESS_NOTIFIED
            )
        )

        # FCM 알림 전송
        # self.container.fcm_service.send_notification()

    def _create_generated_images(
            self,
            image_generation_jobs: List[ImageGenerationJob],
            generation_request_id: int
    ) -> List[GeneratedImage]:
        """생성된 이미지 처리 및 저장"""
        if not image_generation_jobs:
            raise ValueError("No image generation jobs provided")

        generation_request = self.generation_request_repo.get(generation_request_id)

        # 썸네일 이미지 생성 및 업로드
        thumbnail_s3_key = self._create_thumbnail(image_generation_jobs[:3])

        # 이미지 그룹 생성
        image_group = self.generated_image_group_repo.create(
            obj_in=GeneratedImageGroupCreate(
                user_id=generation_request.user_id,
                generation_request_id=generation_request_id,
                thumbnail_image_s3_key=thumbnail_s3_key
            )
        )

        # 개별 이미지 생성
        return [
            self.generated_image_repo.create(
                obj_in=GeneratedImageCreate(
                    user_id=generation_request.user_id,
                    s3_key=job.s3_key,
                    webui_png_info=job.webui_png_info,
                    generated_image_group_id=image_group.id,
                    image_generation_job_id=job.id
                )
            )
            for job in image_generation_jobs
        ]

    def _create_thumbnail(self, jobs: List[ImageGenerationJob]) -> str:
        """썸네일 이미지 생성"""
        image_urls = [
            self.container.s3_client.create_presigned_url(job.s3_key)
            for job in jobs
        ]

        img_bytes, img_format = concatenate_images_horizontally(image_urls)
        compressed_bytes, img_format = compress_and_resize_image(img_bytes)

        thumbnail_key = generate_unique_datatime_uuid_key(
            prefix=aws_s3_setting.GENERATED_IMAGE_GROUP_S3KEY_PREFIX
        )

        self.container.s3_client.upload_to_s3(thumbnail_key, compressed_bytes, img_format)
        return thumbnail_key