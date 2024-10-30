from fastapi import Depends

from app.core.errors.http_exceptions import ValueException, UnauthorizedException
from app.domain.generation.models.image import GeneratedImageGroup
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupUpdate, GeneratedImageGroupInDB
from app.infrastructure.repositories.generation.generation import GeneratedImageGroupRepository, \
    get_generated_image_group_repository


class ImageGroupApplicationService:
    def __init__(
            self,
            generated_image_group_repo: GeneratedImageGroupRepository,
    ):
        self.generated_image_group_repo = generated_image_group_repo

    def update_rating_on_generated_image_group(self, generated_image_group_id: int, rating: int, user_id: int) -> bool:
        generated_image_group: GeneratedImageGroup = self.generated_image_group_repo.get(generated_image_group_id)
        if generated_image_group.user_id != user_id:
            raise UnauthorizedException()

        if rating < 0 or rating > 5:
            raise ValueException("rating should be 0 to 5")

        self.generated_image_group_repo.update(
            obj_id=generated_image_group_id,
            obj_in=GeneratedImageGroupUpdate(rating=rating)
        )
        return True

def get_image_group_application_service(
        generated_image_group_repo: GeneratedImageGroupRepository = Depends(get_generated_image_group_repository)
) -> ImageGroupApplicationService:
    return ImageGroupApplicationService(generated_image_group_repo=generated_image_group_repo)