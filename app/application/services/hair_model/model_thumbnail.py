from typing import List
from fastapi import Depends

from app.application.services.hair_model.dto.model_thumbnail import ModelThumbnailData
from app.domain.hair_model.models.model_thumbnail import ModelThumbnail
from app.infrastructure.repositories.hair_model.model_thumbnail import ModelThumbnailRepository, \
    get_model_thumbnail_repository
from app.infrastructure.s3.s3_client import S3Client, get_s3_client


class ModelThumbnailQueryService:
    def __init__(
            self,
            model_thumbnail_repo: ModelThumbnailRepository,
            s3_client: S3Client
    ):
        self.model_thumbnail_repo = model_thumbnail_repo
        self.s3_client = s3_client

    def get_all_button_thumbnail_images(self) -> List[ModelThumbnailData]:
        db_model_thumbnail_list: List[ModelThumbnail] = self.model_thumbnail_repo.get_all_in_order()
        return [
           ModelThumbnailData(
               presigned_image_url=self.s3_client.create_presigned_url(db_model_thumbnail.s3_key),
               gender_id=db_model_thumbnail.gender_id
           ) for db_model_thumbnail in db_model_thumbnail_list
        ]

def get_model_thumbnail_query_service(
        model_thumbnail_repo: ModelThumbnailRepository = Depends(get_model_thumbnail_repository),
        s3_client: S3Client = Depends(get_s3_client)
) -> ModelThumbnailQueryService:
    return ModelThumbnailQueryService(
        model_thumbnail_repo=model_thumbnail_repo,
        s3_client=s3_client
    )