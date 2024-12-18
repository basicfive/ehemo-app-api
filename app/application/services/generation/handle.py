import json
import logging
from typing import List

from app import fcm_consts
from app.application.services.generation.dto.mq import MQConsumeMessage
from app.application.services.transactional_service import TransactionalService
from app.core.config import aws_s3_settings
from app.core.db.base import get_db
from app.domain.generation.models.enums.generation_status import GenerationStatusEnum, GenerationResultEnum
from app.core.utils import generate_unique_datatime_uuid_key, concatenate_images_horizontally, compress_and_resize_image
from app.domain.generation.models.generation import ImageGenerationJob, GenerationRequest
from app.domain.generation.schemas.generated_image import GeneratedImageCreate
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupCreate
from app.domain.generation.schemas.generation_request import GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobUpdate
from app.domain.generation.services.generation_domain_service import should_create_image_group
from app.domain.hair_model.models.hair import HairStyle
from app.domain.user.models.user import User
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.fcm.dto.fcm_message import FCMGenerationResultData
from app.infrastructure.fcm.fcm_service import FCMService, get_fcm_service
from app.infrastructure.repositories.generation.generation import (
    GenerationRequestRepository,
    ImageGenerationJobRepository,
    GeneratedImageRepository,
    GeneratedImageGroupRepository, get_generation_request_repository, get_image_generation_job_repository,
    get_generated_image_repository, get_generated_image_group_repository
)
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository
from app.infrastructure.s3.s3_client import S3Client, get_s3_client

logger = logging.getLogger(__name__)


class MessageHandler(TransactionalService):
    """메시지 처리를 위한 핸들러"""
    def __init__(
            self,
            generation_request_repo: GenerationRequestRepository,
            image_generation_job_repo: ImageGenerationJobRepository,
            generated_image_repo: GeneratedImageRepository,
            generated_image_group_repo: GeneratedImageGroupRepository,
            user_repo: UserRepository,
            s3_client: S3Client,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.generation_request_repo = generation_request_repo
        self.image_generation_job_repo = image_generation_job_repo
        self.generated_image_repo = generated_image_repo
        self.generated_image_group_repo = generated_image_group_repo
        self.user_repo = user_repo
        self.s3_client = s3_client
        self.fcm_service = fcm_service

    @transactional
    def process_message(self, body: bytes) -> None:
        """메시지 처리의 메인 엔트리포인트"""
        try:
            data_dict = json.loads(body)
            message = MQConsumeMessage(**data_dict)

            logger.info(f"[MQ] Consumed Job ID: {message.image_generation_job_id}. DETAILS: {message.to_str()}")

            image_generation_job = self._update_generation_job(message)

            generation_request = self.generation_request_repo.get(image_generation_job.generation_request_id)
            image_generation_job_list = self.image_generation_job_repo.get_all_by_generation_request(
                generation_request_id=image_generation_job.generation_request_id
            )
            if should_create_image_group(generation_request, image_generation_job_list):
                self._create_and_notify_image_group(generation_request.id, image_generation_job_list)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise

    def _update_generation_job(self, message: MQConsumeMessage) -> ImageGenerationJob:
        return self.image_generation_job_repo.update_with_flush(
            obj_id=message.image_generation_job_id,
            obj_in=ImageGenerationJobUpdate(
                webui_png_info=message.webui_png_info,
                status=GenerationStatusEnum.COMPLETED
            )
        )

    def _create_and_notify_image_group(
            self,
            generation_request_id: int,
            image_generation_jobs: List[ImageGenerationJob]
    ) -> None:
        """이미지 그룹 생성 및 알림 처리"""

        generation_request_with_relation = self.generation_request_repo.get_with_all_relations(generation_request_id)

        # 이미지 및 그룹 생성
        self._create_generated_images(
            generation_request_with_relation,
            image_generation_jobs,
        )

        # 알림 상태 업데이트
        self.generation_request_repo.update(
            obj_id=generation_request_with_relation.id,
            obj_in=GenerationRequestUpdate(
                generation_result=GenerationResultEnum.SUCCEED
            )
        )

        user: User = self.user_repo.get(generation_request_with_relation.user_id)

        # FCM 알림 전송
        # TODO: user fcm token null 값이면 어떻게 동작하지?
        fcm_data = FCMGenerationResultData(generation_status=GenerationResultEnum.SUCCEED)
        self.fcm_service.send_to_token(
            token=user.fcm_token,
            title=fcm_consts.SUCCESS_TITLE,
            body=fcm_consts.SUCCESS_BODY,
            category=fcm_consts.CATEGORY,
            identifier=fcm_consts.IDENTIFIER_PREFIX + str(generation_request_id),
            data=fcm_data.to_fcm_data(),
        )

    def _create_generated_images(
            self,
            generation_request_with_relation: GenerationRequest,
            image_generation_jobs: List[ImageGenerationJob],
    ):
        """생성된 이미지 처리 및 저장"""

        # 썸네일 이미지 생성 및 업로드
        thumbnail_s3_key = self._create_thumbnail(image_generation_jobs[:3])
        hair_style: HairStyle = generation_request_with_relation.hair_variant_model.hair_style

        # 이미지 그룹 생성
        image_group = self.generated_image_group_repo.create_with_flush(
            obj_in=GeneratedImageGroupCreate(
                user_id=generation_request_with_relation.user_id,
                generation_request_id=generation_request_with_relation.id,
                thumbnail_image_s3_key=thumbnail_s3_key,
                title=hair_style.title
            )
        )

        # 개별 이미지 생성
        for job in image_generation_jobs:
            self.generated_image_repo.create(
                obj_in=GeneratedImageCreate(
                    user_id=generation_request_with_relation.user_id,
                    s3_key=job.s3_key,
                    webui_png_info=job.webui_png_info,
                    generated_image_group_id=image_group.id,
                    image_generation_job_id=job.id
                )
            )

    def _create_thumbnail(self, jobs: List[ImageGenerationJob]) -> str:
        """썸네일 이미지 생성"""
        image_urls = [
            self.s3_client.create_presigned_url(job.s3_key)
            for job in jobs
        ]

        img_bytes, img_format = concatenate_images_horizontally(image_urls)
        compressed_bytes, img_format = compress_and_resize_image(img_bytes)

        thumbnail_key = generate_unique_datatime_uuid_key(
            prefix=aws_s3_settings.GENERATED_IMAGE_GROUP_S3KEY_PREFIX
        )

        self.s3_client.upload_to_s3(thumbnail_key, compressed_bytes, img_format)
        return thumbnail_key


def handle_message(body: bytes) -> None:
    db = next(get_db())
    try:
        message_handler = MessageHandler(
            generation_request_repo=get_generation_request_repository(db),
            image_generation_job_repo=get_image_generation_job_repository(db),
            generated_image_repo=get_generated_image_repository(db),
            generated_image_group_repo=get_generated_image_group_repository(db),
            user_repo=get_user_repository(db),
            s3_client=get_s3_client(),
            fcm_service=get_fcm_service(),
            unit_of_work=get_unit_of_work(db),
        )
        message_handler.process_message(body)
    finally:
        db.close()
