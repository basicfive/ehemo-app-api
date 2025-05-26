from typing import List, Tuple, Optional

from app.domain.training.services.training_steps_calculator import calculate_training_epoch
from app.domain.common.enums.gender import Gender
from app.domain.user.models.user import User
from datetime import datetime, UTC, timedelta
from app.core.config import training_settings, image_generation_settings
from app.domain.training.models.training import TrainingRequest, TrainingJob
from app.domain.training.schemas.training.training_request import TrainingRequestCreate
from app.domain.training.schemas.training.training_job import TrainingJobCreate
from app.domain.training.models.image import UploadedImageForTraining
from app.domain.training.schemas.image.uploaded_images_for_training import UploadedImagesForTrainingCreate
from app.domain.training.enums.training_status import TrainingRequestStatus, TrainingJobStatus
from app.domain.training.models.user_hair_style import UserHairStyle
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleCreate
from app.domain.training.services.thumbnail_generation import create_user_hair_style_thumbnail_s3_key
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository
from app.infrastructure.repositories.training.training import TrainingRequestRepository, TrainingJobRepository
from app.infrastructure.repositories.training.image import UploadedImageForTrainingRepository
from app.domain.training.services.thumbnail_generation import get_thumbnail_image_size


def is_register_concluded(status: TrainingRequestStatus) -> bool:
    return status == TrainingRequestStatus.SUCCEEDED or status == TrainingRequestStatus.FAILED


class TrainingRequestService:
    def __init__(
            self,
            training_request_repo: TrainingRequestRepository,
            training_job_repo: TrainingJobRepository,
            user_hair_style_repo: UserHairStyleRepository,
            uploaded_images_for_training_repo: UploadedImageForTrainingRepository,
        ):
        self.training_request_repo = training_request_repo
        self.training_job_repo = training_job_repo
        self.user_hair_style_repo = user_hair_style_repo
        self.uploaded_images_for_training_repo = uploaded_images_for_training_repo

    def is_user_training_request_pending(self, user_id: int) -> bool:
        training_request: Optional[TrainingRequest] = self.training_request_repo.get_latest_training_request_by_user(user_id)
        if training_request and not is_register_concluded(training_request.status):
            return True
        return False
    
    def _calculate_pending_training_jobs_total_steps(self) -> int:
        pending_training_jobs: List[TrainingJob] = self.training_job_repo.get_pending_training_jobs()

        total_steps: int = 0
        for training_job in pending_training_jobs:
            total_steps += training_job.total_steps

        return int(total_steps)
    
    def calculate_training_request_eta_sec(self, current_job_total_steps: int) -> int:
        """
        현재 학습 중인 모델의 진행 상황을 고려하지 않고(아예 새로 시작해야한다고 가정) 예상 시간을 계산함.
        예상 시간 = ((현재 학습 중인 모델의 총 스텝 * 평균 스텝당 소요 시간) + 썸네일 생성 시간 + 업스케일 시간) * 여유 버퍼 (1.1)
        """
        pending_total_steps: int = self._calculate_pending_training_jobs_total_steps()
        return (
            int((pending_total_steps + current_job_total_steps) * training_settings.TIME_PER_STEP_ON_A100_SEC)
            + image_generation_settings.SINGLE_INFERENCE_SEC_EST
            + image_generation_settings.SINGLE_INFERENCE_UPSCALE_SEC_EST
        ) * training_settings.TRAINING_JOB_EXPIRE_TIME_MULTIPLIER

    def create_training_request_and_job(
            self,
            gender: Gender,
            user: User,
            title: str,
            description: str,
            uploaded_images_s3_keys: List[str],
            thumbnail_prompt: str,
        ) -> Tuple[TrainingRequest, List[UploadedImageForTraining], TrainingJob, UserHairStyle]:

        # 1. 학습 요청 생성
        training_request: TrainingRequest = self.training_request_repo.create_with_flush(
            obj_in=TrainingRequestCreate(
                user_id=user.id,
                gender=gender,
                title=title,
                description=description,
                status=TrainingRequestStatus.PENDING,
            )
        )

        # 2. 이미지 레코드 추가
        images_for_training: List[UploadedImageForTraining] = []
        for uploaded_image_s3_key in uploaded_images_s3_keys:
            image_for_training: UploadedImageForTraining = self.uploaded_images_for_training_repo.create_with_flush(
                obj_in=UploadedImagesForTrainingCreate(
                    user_id=user.id,
                    s3_key=uploaded_image_s3_key,
                    training_request_id=training_request.id,
                )
            )
            images_for_training.append(image_for_training)

        image_count: int = len(uploaded_images_s3_keys)
        epoch: int = calculate_training_epoch(image_count)
        total_steps: int = epoch * image_count
        estimated_time_sec: int = self.calculate_training_request_eta_sec(current_job_total_steps=total_steps)

        thumbnail_width, thumbnail_height = get_thumbnail_image_size()

        # 3. 학습 작업 생성
        training_job: TrainingJob = self.training_job_repo.create_with_flush(
            obj_in=TrainingJobCreate(
                expires_at=datetime.now(UTC) + timedelta(seconds=estimated_time_sec),
                training_request_id=training_request.id,
                gender=gender,
                status=TrainingJobStatus.PENDING,
                requested_at=datetime.now(UTC),
                total_steps=total_steps,
                image_count=image_count,
                epoch=epoch,
                thumbnail_s3_key=create_user_hair_style_thumbnail_s3_key(),
                thumbnail_prompt=thumbnail_prompt,
                thumbnail_width=thumbnail_width,
                thumbnail_height=thumbnail_height,
            )
        )

        user_hair_styles: List[UserHairStyle] = self.user_hair_style_repo.get_all_active_by_user(user_id=user.id)
        user_hair_style_order: int = len(user_hair_styles) + 1

        # 4. 헤어스타일 생성
        user_hair_style: UserHairStyle = self.user_hair_style_repo.create_with_flush(
            obj_in=UserHairStyleCreate(
                user_id=user.id,
                gender=gender,
                thumbnail_s3_key=training_job.thumbnail_s3_key,
                title=title,
                description=description,
                order=user_hair_style_order,
                training_request_id=training_request.id,
            )
    )

        return training_request, images_for_training, training_job, user_hair_style


from fastapi import Depends
from app.infrastructure.repositories.training.training import get_training_request_repository
from app.infrastructure.repositories.training.training import get_training_job_repository
from app.infrastructure.repositories.training.image import get_uploaded_image_for_training_repository
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository

def get_training_request_service(
        training_request_repo: TrainingRequestRepository = Depends(get_training_request_repository),
        training_job_repo: TrainingJobRepository = Depends(get_training_job_repository),
        user_hair_style_repo: UserHairStyleRepository = Depends(get_user_hair_style_repository),
        uploaded_images_for_training_repo: UploadedImageForTrainingRepository = Depends(get_uploaded_image_for_training_repository),
) -> TrainingRequestService:
    return TrainingRequestService(
        training_request_repo=training_request_repo,
        training_job_repo=training_job_repo,
        user_hair_style_repo=user_hair_style_repo,
        uploaded_images_for_training_repo=uploaded_images_for_training_repo,
    )