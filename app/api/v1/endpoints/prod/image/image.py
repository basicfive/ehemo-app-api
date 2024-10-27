from fastapi import Depends, APIRouter
from typing import List

from app.application.services.image.dto.generated_image import GeneratedImageData, GeneratedImageGroupData
from app.application.services.image.generated_image import GeneratedImageApplicationService, \
    get_generated_image_application_service

router = APIRouter()

"""
여기서 return 값도 dto로 묶어야할까? 라는 의문이 있다.
request가 존재하는 목적은 id 값을 받아 schema 정의가 안되어있는 값들을 가져올때.
보통 반환 값들은 service 에서 dto(InDB)로 반환하도록 처리가 되기에...
"""

# /api/v1/prod/image
@router.get("/images")
def get_image_by_group(
        generated_image_group_id: int,
        service: GeneratedImageApplicationService = Depends(get_generated_image_application_service)
) -> List[GeneratedImageData]:
    return service.get_generated_image_list_by_image_group(generated_image_group_id=generated_image_group_id)

@router.get("/image_groups")
def get_image_groups_by_user(
        user_id: int,
        service:  GeneratedImageApplicationService = Depends(get_generated_image_application_service)
) -> List[GeneratedImageGroupData]:
    return service.get_generated_image_group_list_by_user(user_id=user_id)



