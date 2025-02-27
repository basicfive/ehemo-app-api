from fastapi import Depends

from app import aws_s3_settings
from app.application.services.image.dto.background_update import LastModifiedImageUploadDto
from app.application.services.transactional_service import TransactionalService
from app.core.errors.http_exceptions import AccessUnauthorizedException
from app.core.utils import generate_unique_datatime_uuid_key
from app.domain import GeneratedImage
from app.domain.generation.schemas.generated_image import GeneratedImageUpdate
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.generation.generation import GeneratedImageRepository, \
    get_generated_image_repository
from app.infrastructure.s3.s3_client import S3Client, get_s3_client


class GeneratedImageBackgroundUpdateService(TransactionalService):
    def __init__(
            self,
            generated_image_repo: GeneratedImageRepository,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.generated_image_repo = generated_image_repo
        self.s3_client = s3_client

    def create_update_presigned_url(self, generated_image_id: int, user_id: int) -> LastModifiedImageUploadDto:
        # validation
        generated_image: GeneratedImage = self.generated_image_repo.get(obj_id=generated_image_id)
        if generated_image.user_id != user_id:
            raise AccessUnauthorizedException()

        s3_key = generate_unique_datatime_uuid_key(prefix=aws_s3_settings.GENERATED_IMAGE_S3KEY_PREFIX)
        upload_presigned_url = self.s3_client.create_put_presigned_url(s3_key=s3_key, content_type="image/jpeg")

        return LastModifiedImageUploadDto(
            generated_image_id=generated_image_id,
            upload_presigned_url=upload_presigned_url,
            s3_key=s3_key,
        )

    @transactional
    def update_latest_modified_image_key(self, request: LastModifiedImageUploadDto, user_id: int):
        generated_image: GeneratedImage = self.generated_image_repo.get(obj_id=request.generated_image_id)
        if generated_image.user_id != user_id:
            raise AccessUnauthorizedException()

        self.generated_image_repo.update(
            obj_id=generated_image.id,
            obj_in=GeneratedImageUpdate(
                last_modified_image_key=request.s3_key,
            )
        )

def get_generated_image_background_update_service(
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        s3_client: S3Client = Depends(get_s3_client),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> GeneratedImageBackgroundUpdateService:
    return GeneratedImageBackgroundUpdateService(
        generated_image_repo=generated_image_repo,
        s3_client=s3_client,
        unit_of_work=unit_of_work,
    )
