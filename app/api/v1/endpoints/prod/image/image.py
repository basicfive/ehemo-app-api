from fastapi import Depends, APIRouter
from typing import List
from app.api.v1.endpoints.prod.image.dto import ImageByGroupRequest, ImageGroupByUserRequest
from app.application.services.image.generated_image import GeneratedImageApplicationService, \
    get_generated_image_application_service
from app.domain.generation.schemas.generated_image import GeneratedImageInDB
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupInDB

router = APIRouter()

"""
여기서 return 값도 dto로 묶어야할까? 라는 의문이 있다.
request가 존재하는 목적은 id 값을 받아 schema 정의가 안되어있는 값들을 가져올때.
보통 반환 값들은 service 에서 dto(InDB)로 반환하도록 처리가 되기에...
"""

# /api/v1/prod/image
@router.get("/images")
def get_image_by_group(
        request: ImageByGroupRequest,
        service: GeneratedImageApplicationService = Depends(get_generated_image_application_service)
) -> List[GeneratedImageInDB]:
    return service.get_generated_image_list_by_image_group(generated_image_group_id=request.generated_image_group_id)

@router.get("/image_groups")
def get_image_groups_by_user(
        request: ImageGroupByUserRequest,
        service:  GeneratedImageApplicationService = Depends(get_generated_image_application_service)
) -> List[GeneratedImageGroupInDB]:
    return service.get_generated_image_group_list_by_user(user_id=request.user_id)



