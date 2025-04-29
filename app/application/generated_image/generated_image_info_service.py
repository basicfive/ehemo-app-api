from typing import List

from app.application.generated_image.dto.generated_image_info import GeneratedImageData
from app.domain.generation.enums.generated_image_status import GeneratedImageStatus

from app.infrastructure.repositories.generation.generated_image import GeneratedImageRepository
from app.infrastructure.s3.s3_client import S3Client

class GeneratedImageInfoService:
    def __init__(
            self,
            generated_image_repo: GeneratedImageRepository,
            s3_client: S3Client,
        ):
        self.generated_image_repo = generated_image_repo
        self.s3_client = s3_client
    
    def get_user_generated_images(self, user_id: int) -> List[GeneratedImageData]:
        generated_images = self.generated_image_repo.get_user_generated_images(user_id)
        return sorted([
            GeneratedImageData(
                id=generated_image.id,
                status=generated_image.status,
                image_url=self.s3_client.create_get_presigned_url(generated_image.upscaled_s3_key),
                s3_key=generated_image.upscaled_s3_key,
                generation_job_id=generated_image.generation_job_id,
                created_at=generated_image.created_at,
            ) for generated_image in generated_images
        ], key=lambda x: x.created_at, reverse=True)

from fastapi import Depends
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.s3.s3_client import get_s3_client

def get_generated_image_info_service(
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        s3_client: S3Client = Depends(get_s3_client),
    ) -> GeneratedImageInfoService:
        return GeneratedImageInfoService(
            generated_image_repo=generated_image_repo,
            s3_client=s3_client,
        )
