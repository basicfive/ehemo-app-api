from typing import List

from app.application.transactional_service import TransactionalService
from app.application.generated_image.dto.generated_image_info import GeneratedImageData
from app.infrastructure.repositories.generation.generated_image import GeneratedImageRepository
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository
from app.infrastructure.s3.s3_client import S3Client
from app.domain.generation.models.generation import GenerationRequest
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.database.transaction import transactional
from app.core.errors.http_exceptions import AccessUnauthorizedException
from app.domain.generation.schemas.generated_image.generated_image import GeneratedImageUpdate
from app.domain.generation.enums.generated_image_status import GeneratedImageStatus
from app.domain.generation.models.generated_image import GeneratedImage

class GeneratedImageService(TransactionalService):
    def __init__(
            self,
            generated_image_repo: GeneratedImageRepository,
            generation_request_repo: GenerationRequestRepository,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
        ):
        super().__init__(unit_of_work)
        self.generated_image_repo = generated_image_repo
        self.generation_request_repo = generation_request_repo
        self.s3_client = s3_client

    def _convert_to_generated_image_data(self, generated_images: List[GeneratedImage]) -> List[GeneratedImageData]:
        return sorted([
            GeneratedImageData(
                id=generated_image.id,
                image_url=self.s3_client.create_get_presigned_url(generated_image.upscaled_s3_key),
                s3_key=generated_image.upscaled_s3_key,
                generation_request_id=generated_image.generation_job.generation_request_id,
                created_at=generated_image.created_at,
            ) for generated_image in generated_images
        ], key=lambda x: x.created_at, reverse=True)
    
    def get_upscaled_user_generated_images(self, user_id: int) -> List[GeneratedImageData]:
        generated_images: List[GeneratedImage] = self.generated_image_repo.get_upscaled_user_generated_images_with_job(user_id)
        return self._convert_to_generated_image_data(generated_images)
    
    def get_images_by_request_id(self, request_id: int, user_id: int) -> List[GeneratedImageData]:
        generation_request: GenerationRequest = self.generation_request_repo.get(request_id)
        if generation_request.user_id != user_id:
            raise AccessUnauthorizedException()

        generated_images: List[GeneratedImage] = self.generated_image_repo.get_all_by_generation_request_id(request_id)
        return self._convert_to_generated_image_data(generated_images)

    @transactional
    def report_images(self, user_id: int, image_ids: List[int]):
        images: List[GeneratedImage] = self.generated_image_repo.get_all_in(image_ids)
        for image in images:
            if image.user_id != user_id:
                raise AccessUnauthorizedException()
            self.generated_image_repo.update(
                obj_id=image.id,
                obj_in=GeneratedImageUpdate(
                    status=GeneratedImageStatus.REPORTED,
                )
            )
    
    @transactional
    def delete_images(self, user_id: int, image_ids: List[int]):
        images: List[GeneratedImage] = self.generated_image_repo.get_all_in(image_ids)
        for image in images:
            if image.user_id != user_id:
                raise AccessUnauthorizedException()
            self.generated_image_repo.update(
                obj_id=image.id,
                obj_in=GeneratedImageUpdate(
                    status=GeneratedImageStatus.DELETED,
                )
            )


from fastapi import Depends
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.s3.s3_client import get_s3_client
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.repositories.generation.generation import get_generation_request_repository

def get_generated_image_service(
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        s3_client: S3Client = Depends(get_s3_client),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    ) -> GeneratedImageService:
        return GeneratedImageService(
            generated_image_repo=generated_image_repo,
            generation_request_repo=generation_request_repo,
            s3_client=s3_client,
            unit_of_work=unit_of_work,
        )
