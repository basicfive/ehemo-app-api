from typing import List, Tuple, Optional

from app.domain.training.schemas.training.training_job import TrainingJobUpdate
from app.domain.training.services.training_steps_calculator import calculate_training_epoch
from app.domain.common.enums.gender import Gender
from app.domain.user.models.user import User
from datetime import datetime
from app.core.config import training_settings
from app.domain.training.models.training import TrainingRequest, TrainingJob
from app.domain.training.schemas.training.training_request import TrainingRequestCreate
from app.domain.training.schemas.training.training_job import TrainingJobCreate
from app.domain.training.schemas.image.training_request_uploaded_images import TrainingRequestUploadedImagesCreate
from app.domain.training.models.image import UploadedImagesForTraining
from app.domain.training.schemas.image.uploaded_images_for_training import UploadedImagesForTrainingCreate
from app.domain.common.enums.ai_status import TrainingRequestStatus, TrainingJobStatus

from app.infrastructure.repositories.training.training import TrainingRequestRepository, TrainingJobRepository
from app.infrastructure.repositories.training.image import TrainingRequestUploadedImagesRepository, UploadedImagesForTrainingRepository


class TrainingRequestService:
    def __init__(
            self,
            training_request_repository: TrainingRequestRepository,
            training_job_repository: TrainingJobRepository,
            training_request_uploaded_images_repository: TrainingRequestUploadedImagesRepository,
            uploaded_images_for_training_repository: UploadedImagesForTrainingRepository,
        ):
        self.training_request_repository = training_request_repository
        self.training_job_repository = training_job_repository
        self.training_request_uploaded_images_repository = training_request_uploaded_images_repository
        self.uploaded_images_for_training_repository = uploaded_images_for_training_repository

    def is_user_training_job_pending(self, user_id: int) -> bool:
        training_job: Optional[TrainingJob] = self.training_job_repository.get_latest_training_job_by_user(user_id)
        if training_job and training_job.status == TrainingJobStatus.PENDING:
            return True
        return False
    
    def get_training_request_with_user_by_training_job(self, training_job_id: int) -> TrainingRequest:
        training_job: TrainingJob = self.training_job_repository.get_with_request_with_user(training_job_id)
        return training_job.training_request
    
    def calculate_training_request_eta_sec(self) -> int:
        # 현재 학습 중인 모델의 진행 상황을 고려하지 않고(아예 새로 시작해야한다고 가정) 예상 시간을 계산함.
        pending_training_jobs: List[TrainingJob] = self.training_job_repository.get_pending_training_jobs()

        total_steps: int = 0
        for training_job in pending_training_jobs:
            total_steps += training_job.total_steps

        return total_steps * training_settings.TIME_PER_STEP_ON_A100_SEC

    def create_training_request_and_job(
            self,
            gender: Gender,
            user: User,
            title: str,
            description: str,
            uploaded_images_s3_keys: List[str],
        ) -> Tuple[List[UploadedImagesForTraining], TrainingRequest, TrainingJob]:

        # 1. 이미지 레코드 추가
        images_for_training: List[UploadedImagesForTraining] = []
        for uploaded_image_s3_key in uploaded_images_s3_keys:
            image_for_training: UploadedImagesForTraining = self.uploaded_images_for_training_repository.create_with_flush(
                obj_in=UploadedImagesForTrainingCreate(
                    user_id=user.id,
                    s3_key=uploaded_image_s3_key,
                )
            )
            images_for_training.append(image_for_training)
        
        # 2. 학습 요청 생성
        training_request: TrainingRequest = self.training_request_repository.create_with_flush(
            obj_in=TrainingRequestCreate(
                user_id=user.id,
                gender=gender,
                title=title,
                description=description,
                status=TrainingRequestStatus.PENDING,
            )
        )

        image_count: int = len(uploaded_images_s3_keys)
        epoch: int = calculate_training_epoch(image_count)
        total_steps: int = epoch * image_count

        # 3. 학습 작업 생성
        training_job: TrainingJob = self.training_job_repository.create_with_flush(
            obj_in=TrainingJobCreate(
                training_request_id=training_request.id,
                gender=gender,
                status=TrainingJobStatus.PENDING,
                requested_at=datetime.now(),
                total_steps=total_steps,
                image_count=image_count,
                epoch=epoch,
            )
        )

        # 4. 이미지 - 학습 요청 n : m 관계 생성
        for image_for_training in images_for_training:
            self.training_request_uploaded_images_repository.create_with_flush(
                obj_in=TrainingRequestUploadedImagesCreate(
                    training_request_id=training_request.id,
                    uploaded_images_for_training_id=image_for_training.id,
                )
            )

        return images_for_training, training_request, training_job


from fastapi import Depends
from app.infrastructure.repositories.training.training import get_training_request_repository
from app.infrastructure.repositories.training.training import get_training_job_repository
from app.infrastructure.repositories.training.image import get_training_request_uploaded_images_repository
from app.infrastructure.repositories.training.image import get_uploaded_images_for_training_repository

def get_training_request_service(
        training_request_repository: TrainingRequestRepository = Depends(get_training_request_repository),
        training_job_repository: TrainingJobRepository = Depends(get_training_job_repository),
        training_request_uploaded_images_repository: TrainingRequestUploadedImagesRepository = Depends(get_training_request_uploaded_images_repository),
        uploaded_images_for_training_repository: UploadedImagesForTrainingRepository = Depends(get_uploaded_images_for_training_repository),
) -> TrainingRequestService:
    return TrainingRequestService(
        training_request_repository=training_request_repository,
        training_job_repository=training_job_repository,
        training_request_uploaded_images_repository=training_request_uploaded_images_repository,
        uploaded_images_for_training_repository=uploaded_images_for_training_repository,
    )