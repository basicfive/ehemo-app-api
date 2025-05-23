import json
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
