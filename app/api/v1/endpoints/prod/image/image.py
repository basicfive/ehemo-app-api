from fastapi import Depends, APIRouter
from typing import List

from app.application.services.image.dto.generated_image import GeneratedImageData, GeneratedImageGroupData
from app.application.services.image.image_group import ImageGroupApplicationService, get_image_group_application_service
from app.application.services.image.image_query import ImageQueryApplicationService, \
    get_generated_image_application_service
from app.application.services.user.user_auth import validate_user_token

router = APIRouter()

# /api/v1/prod/image/

@router.get("/images")
def get_image_by_group(
        generated_image_group_id: int,
        user_id: int = Depends(validate_user_token),
        service: ImageQueryApplicationService = Depends(get_generated_image_application_service)
) -> List[GeneratedImageData]:
    return service.get_generated_image_list_by_image_group(
        generated_image_group_id=generated_image_group_id,
        user_id=user_id
    )

@router.get("/image_groups")
def get_image_groups_by_user(
        user_id: int = Depends(validate_user_token),
        service: ImageQueryApplicationService = Depends(get_generated_image_application_service)
) -> List[GeneratedImageGroupData]:
    return service.get_generated_image_group_list_by_user(user_id=user_id)

@router.post("/{generated_image_group_id}/rating")
def update_rating_on_generated_image_group(
        generated_image_group_id: int,
        rating: int,
        user_id: int = Depends(validate_user_token),
        service: ImageGroupApplicationService = Depends(get_image_group_application_service)
) -> bool:
    return service.update_rating_on_generated_image_group(
        rating=rating,
        generated_image_group_id=generated_image_group_id,
        user_id=user_id
    )

