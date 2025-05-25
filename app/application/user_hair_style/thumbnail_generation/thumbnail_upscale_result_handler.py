import json
import logging
from typing import Tuple

from app.application.user_hair_style.thumbnail_generation.dto.thumbnail_mq import ThumbnailUpscaleConsumeMessage

from app.application.generation.request.dto.upscale_mq import UpscaleImageInfo
from app.domain.training.models.user_hair_style import UserHairStyle
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleCreate
from app.domain.training.enums.training_status import TrainingJobStatus, TrainingRequestStatus
from app.infrastructure.database.transaction import transactional
from app.application.transactional_service import TransactionalService
from app.domain.training.models.training import TrainingJob, TrainingRequest
from app.domain.training.schemas.training.training_job import TrainingJobUpdate
from app.domain.training.schemas.training.training_request import TrainingRequestUpdate
from app.infrastructure.repositories.training.training import TrainingJobRepository, TrainingRequestRepository
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.s3.s3_client import S3Client
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleUpdate
from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus
from app.domain.user.models.user import User
from app.core.constants import FCMConstants
from app.infrastructure.repositories.user.user import UserRepository
from app.core.utils import convert_image_to_webp_from_url

class ThumbnailUpscaleResultHandler(TransactionalService):
    def __init__(
            self,
            training_job_repo: TrainingJobRepository,
            training_request_repo: TrainingRequestRepository,
            user_hair_style_repo: UserHairStyleRepository,
            user_repo: UserRepository,
            s3_client: S3Client,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
        ):
        super().__init__(unit_of_work)
        self.training_job_repo = training_job_repo
        self.training_request_repo = training_request_repo
        self.user_hair_style_repo = user_hair_style_repo
        self.user_repo = user_repo
        self.fcm_service = fcm_service
        self.s3_client = s3_client

    def _convert_thumbnail_to_webp(self, s3_key: str) -> None:
        # S3에서 이미지 다운로드를 위한 presigned URL 생성
        download_url = self.s3_client.create_get_presigned_url(s3_key)
        if not download_url:
            raise Exception(f"Failed to create presigned URL for downloading: {s3_key}")
        
        # 유틸리티 함수를 사용하여 WebP로 변환
        webp_bytes = convert_image_to_webp_from_url(download_url, quality=90)
        
        # 동일한 S3 키에 WebP 이미지 업로드
        upload_success = self.s3_client.upload_to_s3(
            key=s3_key,
            image_data=webp_bytes,
            image_format='WEBP'
        )
        
        if not upload_success:
            raise Exception(f"Failed to upload WebP thumbnail: {s3_key}")

    @transactional
    def mark_after_upscale_failure(self, training_job_id: int) -> TrainingJob:
        # 썸네일 제작으로 인한 실패는 썸네일 제작 실패 카운트만 증가시키고 끝내면 됨. (헤어스타일 / request 에 대한 실패처리는 재시도 로직에서 다룰 것)
        training_job: TrainingJob = self.training_job_repo.get(training_job_id)
        return self.training_job_repo.update_with_flush(
            obj_id=training_job_id,
            obj_in=TrainingJobUpdate(
                thumbnail_creation_failure_count=training_job.thumbnail_creation_failure_count + 1,
            )
        )
    
    @transactional
    def mark_after_upscale_success(self, training_job_id: int) -> Tuple[TrainingJob, TrainingRequest, UserHairStyle]:
        training_job: TrainingJob = self.training_job_repo.update_with_flush(
            obj_id=training_job_id,
            obj_in=TrainingJobUpdate(
                status=TrainingJobStatus.COMPLETED,
            ),
        )

        training_request: TrainingRequest = self.training_request_repo.update_with_flush(
            obj_id=training_job.training_request_id,
            obj_in=TrainingRequestUpdate(
                status=TrainingRequestStatus.SUCCEEDED,
            ),
        )

        user_hair_style: UserHairStyle = self.user_hair_style_repo.get_by_training_request(training_job.training_request_id)
        self.user_hair_style_repo.update_with_flush(
            obj_id=user_hair_style.id,
            obj_in=UserHairStyleUpdate(
                status=UserHairStyleStatus.REGISTERED,
            )
        )
        return training_job, training_request, user_hair_style

    def _handle_success_and_notify_fcm(self, message: ThumbnailUpscaleConsumeMessage) -> None:
        # transaction
        training_job, training_request, user_hair_style = self.mark_after_upscale_success(message.training_job_id)

        # 썸네일 이미지를 WebP로 변환하여 재업로드
        if training_job.thumbnail_s3_key:
            self._convert_thumbnail_to_webp(training_job.thumbnail_s3_key)

        user: User = self.user_repo.get(training_request.user_id)
       
        self.fcm_service.send_to_token(
            token=user.fcm_token,
            title=FCMConstants.USER_HAIRSTYLE_REGISTER_COMPLETED_TITLE,
            body=FCMConstants.USER_HAIRSTYLE_REGISTER_COMPLETED_BODY,
        )

    def _handle_failure(self, message: ThumbnailUpscaleConsumeMessage) -> None:
        # transaction
        self.mark_after_upscale_failure(message.training_job_id)

    def handle_thumbnail_upscale_result(self, body: bytes) -> None:
        data_dict = json.loads(body)
        message = ThumbnailUpscaleConsumeMessage(**data_dict)

        if message.is_success:
            self._handle_success_and_notify_fcm(message)
        else:
            self._handle_failure(message)


from app.core.db.base import get_db
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.repositories.training.training import get_training_job_repository, get_training_request_repository
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.s3.s3_client import get_s3_client
from app.infrastructure.fcm.fcm_service import get_fcm_service

def handle_thumbnail_upscale_result(body: bytes) -> None:
    db = next(get_db())

    try:
        training_job_repo = get_training_job_repository(db)
        training_request_repo = get_training_request_repository(db)
        user_hair_style_repo = get_user_hair_style_repository(db)
        user_repo = get_user_repository(db)
        s3_client = get_s3_client()
        fcm_service = get_fcm_service()
        unit_of_work = get_unit_of_work(db)

        service = ThumbnailUpscaleResultHandler(
            training_job_repo=training_job_repo,
            training_request_repo=training_request_repo,
            user_hair_style_repo=user_hair_style_repo,
            user_repo=user_repo,
            s3_client=s3_client,
            fcm_service=fcm_service,
            unit_of_work=unit_of_work,
        )
        service.handle_thumbnail_upscale_result(body)
    finally:
        db.close()
