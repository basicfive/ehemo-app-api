from fastapi import Depends, APIRouter, status
from typing import List

from app.application.services.image.background_update import GeneratedImageBackgroundUpdateService, \
    get_generated_image_background_update_service
from app.application.services.image.dto.background_update import LastModifiedImageUploadDto
from app.application.services.image.dto.query import GeneratedImageData, GeneratedImageGroupData
from app.application.services.image.management import ImageManagementApplicationService, get_image_management_application_service
from app.application.services.image.query import ImageQueryApplicationService, \
    get_image_query_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# /api/v1/prod/image/

@router.get("/images/by-group")
def get_image_by_group(
        generated_image_group_id: int,
        user_id: int = Depends(validate_user_token),
        service: ImageQueryApplicationService = Depends(get_image_query_application_service)
) -> List[GeneratedImageData]:
    return service.get_generated_image_list_by_image_group(
        generated_image_group_id=generated_image_group_id,
        user_id=user_id
    )

@router.get("/images/by-request")
def get_image_by_request(
        generation_request_id: int,
        user_id: int = Depends(validate_user_token),
        service: ImageQueryApplicationService = Depends(get_image_query_application_service)
) -> List[GeneratedImageData]:
    return service.get_generated_image_list_by_generation_request(
        generation_request_id=generation_request_id,
        user_id=user_id
    )

@router.get("/image_groups")
def get_image_groups_by_user(
        user_id: int = Depends(validate_user_token),
        service: ImageQueryApplicationService = Depends(get_image_query_application_service)
) -> List[GeneratedImageGroupData]:
    return service.get_generated_image_group_list_by_user(user_id=user_id)

@router.patch("/{generated_image_group_id}/rating")
def update_rating_on_generated_image_group(
        generated_image_group_id: int,
        rating: int,
        user_id: int = Depends(validate_user_token),
        service: ImageManagementApplicationService = Depends(get_image_management_application_service)
) -> bool:
    return service.update_rating_on_generated_image_group(
        rating=rating,
        generated_image_group_id=generated_image_group_id,
        user_id=user_id
    )

@router.patch("/{generated_image_group_id}/report")
def soft_delete_group_and_images(
        generated_image_group_id: int,
        user_id: int = Depends(validate_user_token),
        service: ImageManagementApplicationService = Depends(get_image_management_application_service)
) -> bool:
    return service.report_group_and_images(generated_image_group_id, user_id)

@router.patch("/{generated_image_group_id}/soft-delete")
def soft_delete_group_and_images(
        generated_image_group_id: int,
        user_id: int = Depends(validate_user_token),
        service: ImageManagementApplicationService = Depends(get_image_management_application_service)
) -> bool:
    return service.soft_delete_group_and_images(generated_image_group_id, user_id)

# 배경 수정된 이미지 업로드

@router.get("/modified-img-upload-presigned-url", response_model=LastModifiedImageUploadDto, status_code=status.HTTP_200_OK)
def get_modified_img_upload_presigned_url(
        generated_image_id: int,
        user_id: int = Depends(validate_user_token),
        service: GeneratedImageBackgroundUpdateService = Depends(get_generated_image_background_update_service),
) -> LastModifiedImageUploadDto:
    return service.create_update_presigned_url(generated_image_id, user_id)

@router.put("/latest-modified-image-key", status_code=status.HTTP_201_CREATED)
def update_latest_modified_image_key(
        request: LastModifiedImageUploadDto,
        user_id: int = Depends(validate_user_token),
        service: GeneratedImageBackgroundUpdateService = Depends(get_generated_image_background_update_service),
):
    service.update_latest_modified_image_key(request, user_id)
