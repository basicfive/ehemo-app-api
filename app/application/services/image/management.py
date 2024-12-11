from typing import List

from fastapi import Depends

from app.application.services.transactional_service import TransactionalService
from app.core.errors.http_exceptions import RequestValueException, AccessUnauthorizedException
from app.domain.generation.models.image import GeneratedImageGroup, GeneratedImage
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupUpdate
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.generation.generation import GeneratedImageGroupRepository, \
    get_generated_image_group_repository, GeneratedImageRepository, get_generated_image_repository


class ImageManagementApplicationService(TransactionalService):
    def __init__(
            self,
            generated_image_repo: GeneratedImageRepository,
            generated_image_group_repo: GeneratedImageGroupRepository,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.generated_image_repo = generated_image_repo
        self.generated_image_group_repo = generated_image_group_repo

    @transactional
    def update_rating_on_generated_image_group(self, generated_image_group_id: int, rating: int, user_id: int) -> bool:
        generated_image_group: GeneratedImageGroup = self.generated_image_group_repo.get(generated_image_group_id)
        if generated_image_group.user_id != user_id:
            raise AccessUnauthorizedException()

        if rating < 0 or rating > 5:
            raise RequestValueException("rating should be 0 to 5")

        self.generated_image_group_repo.update(
            obj_id=generated_image_group_id,
            obj_in=GeneratedImageGroupUpdate(rating=rating)
        )
        return True

    @transactional
    def soft_delete_group_and_images(self, generated_image_group_id: int, user_id: int) -> bool:

        generated_image_group: GeneratedImageGroup = self.generated_image_group_repo.get(generated_image_group_id)
        if generated_image_group.user_id != user_id:
            raise AccessUnauthorizedException()

        generated_image_list: List[GeneratedImage] = self.generated_image_repo.get_all_by_generate_image_group(generated_image_group_id)
        generated_image_id_list: List[int] = [generated_image.id for generated_image in generated_image_list]
        self.generated_image_repo.soft_delete_all_in(generated_image_id_list)
        self.generated_image_group_repo.soft_delete(generated_image_group_id)
        return True

def get_image_management_application_service(
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        generated_image_group_repo: GeneratedImageGroupRepository = Depends(get_generated_image_group_repository),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> ImageManagementApplicationService:
    return ImageManagementApplicationService(
        generated_image_repo=generated_image_repo,
        generated_image_group_repo=generated_image_group_repo,
        unit_of_work=unit_of_work,
    )