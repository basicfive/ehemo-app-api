from typing import List, Dict

from app.infrastructure.s3.s3_client import S3Client
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository
from app.domain.training.models.user_hair_style import UserHairStyle
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleInDB
from app.application.user_hair_style.query.dto.query import UserHairStyleInfo
from app.domain.training.models.user_hair_style import UserHairStyleLora
from app.application.user_hair_style.query.dto.query import UserHairStyleDetail
from app.infrastructure.repositories.training.image import UploadedImageForTrainingRepository
from app.domain.training.models.image import UploadedImageForTraining
from app.application.user_hair_style.query.dto.query import UploadedImageData
from app.application.user_hair_style.query.dto.status import RegisterStatus
from app.domain.training.models.training import TrainingJob
from app.infrastructure.repositories.training.training import TrainingJobRepository
from app.core.errors.http_exceptions import AccessUnauthorizedException

class UserHairStyleQueryService:
    def __init__(
            self,
            user_hair_style_repo: UserHairStyleRepository,
            uploaded_images_for_training_repo: UploadedImageForTrainingRepository,
            training_job_repo: TrainingJobRepository,
            s3_client: S3Client,
        ):
        self.user_hair_style_repo = user_hair_style_repo
        self.uploaded_images_for_training_repo = uploaded_images_for_training_repo
        self.training_job_repo = training_job_repo
        self.s3_client = s3_client

    def get_all_user_hair_style_infos(self, user_id: int) -> List[UserHairStyleInfo]:
        user_hair_style_list: List[UserHairStyle] = self.user_hair_style_repo.get_all_active_by_user(user_id)
        user_hair_style_list = sorted(user_hair_style_list, key=lambda x: x.order, reverse=True)

        user_hair_style_infos: List[UserHairStyleInfo] = []
        for user_hair_style in user_hair_style_list:
            user_hair_style_indb = UserHairStyleInDB.model_validate(user_hair_style)

            user_hair_style_infos.append(
                UserHairStyleInfo(
                    **user_hair_style_indb.model_dump(),
                    thumbnail_url=self.s3_client.create_get_presigned_url(user_hair_style_indb.thumbnail_s3_key),
                )
            )

        return user_hair_style_infos


    def get_user_hair_style_info(self, user_hair_style_id: int) -> UserHairStyleInfo:
        user_hair_style: UserHairStyle = self.user_hair_style_repo.get(user_hair_style_id)
        user_hair_style_indb = UserHairStyleInDB.model_validate(user_hair_style)

        return UserHairStyleInfo(
            **user_hair_style_indb.model_dump(),
            thumbnail_url=self.s3_client.create_get_presigned_url(user_hair_style_indb.thumbnail_s3_key),
        )

    def get_user_hair_style_detail(self, user_hair_style_id: int) -> UserHairStyleDetail:
        training_request_id: int = self.user_hair_style_repo.get_training_request_id(user_hair_style_id)
        uploaded_images_for_training: List[UploadedImageForTraining] = (
            self.uploaded_images_for_training_repo.get_all_by_training_request(training_request_id)
        )

        uploaded_image_data_list: List[UploadedImageData] = [
            UploadedImageData(
                s3_key=uploaded_image_for_training.s3_key,
                url=self.s3_client.create_get_presigned_url(uploaded_image_for_training.s3_key),
            )
            for uploaded_image_for_training in uploaded_images_for_training
        ]

        return UserHairStyleDetail(
            id=user_hair_style_id,
            uploaded_image_data_list=uploaded_image_data_list,
        )
    
    def get_pending_user_hair_styles(self, user_id: int) -> List[RegisterStatus]:
        user_hair_style_with_training_request_list: List[UserHairStyle] = (
            self.user_hair_style_repo.get_all_pending_by_user_with_training_request(user_id)
        )

        training_request_ids: List[int] = [user_hair_style.training_request_id for user_hair_style in user_hair_style_with_training_request_list]
        training_jobs: List[TrainingJob] = self.training_job_repo.get_all_by_training_requests(training_request_ids)
        training_job_dict: Dict[int, TrainingJob] = {training_job.training_request_id: training_job for training_job in training_jobs}

        user_hair_style_status_list: List[RegisterStatus] = []
        for user_hair_style in user_hair_style_with_training_request_list:
            training_job: TrainingJob = training_job_dict[user_hair_style.training_request_id]
            user_hair_style_status_list.append(
                RegisterStatus(
                    user_hair_style_id=user_hair_style.id,
                    status=user_hair_style.status,
                    expires_at=training_job.expires_at,
                )
            )

        return user_hair_style_status_list
    
    def get_user_hair_style_status(self, user_hair_style_id: int, user_id: int) -> RegisterStatus:
        user_hair_style: UserHairStyle = self.user_hair_style_repo.get(user_hair_style_id)
        if user_hair_style.user_id != user_id:
            raise AccessUnauthorizedException()

        training_job: TrainingJob = self.training_job_repo.get_by_training_request(user_hair_style.training_request_id)
        return RegisterStatus(
            user_hair_style_id=user_hair_style.id,
            status=user_hair_style.status,
            expires_at=training_job.expires_at,
        )

from fastapi import Depends
from app.infrastructure.s3.s3_client import get_s3_client
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository
from app.infrastructure.repositories.training.image import get_uploaded_image_for_training_repository
from app.infrastructure.repositories.training.training import get_training_job_repository

def get_user_hair_style_query_service(
        user_hair_style_repo: UserHairStyleRepository = Depends(get_user_hair_style_repository),
        uploaded_images_for_training_repo: UploadedImageForTrainingRepository = Depends(get_uploaded_image_for_training_repository),
        training_job_repo: TrainingJobRepository = Depends(get_training_job_repository),
        s3_client: S3Client = Depends(get_s3_client),
    ) -> UserHairStyleQueryService:
    return UserHairStyleQueryService(
        user_hair_style_repo=user_hair_style_repo,
        uploaded_images_for_training_repo=uploaded_images_for_training_repo,
        training_job_repo=training_job_repo,
        s3_client=s3_client,
    )

