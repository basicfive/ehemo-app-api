from fastapi import APIRouter, Depends

from app.application.generated_image.generated_image_info_service import get_generated_image_service
from app.application.generated_image.dto.generated_image_info import GeneratedImageData
from app.application.user.auth import validate_user_token
from typing import List
from app.application.generated_image.generated_image_info_service import GeneratedImageService

router = APIRouter()

@router.get("")
async def get_upscaled_user_generated_images(
    user_id: int = Depends(validate_user_token),
    service: GeneratedImageService = Depends(get_generated_image_service),
) -> List[GeneratedImageData]:
    return service.get_upscaled_user_generated_images(user_id)

@router.get("/by-request/{request_id}")
async def get_images_by_request_id(
    request_id: int,
    user_id: int = Depends(validate_user_token),
    service: GeneratedImageService = Depends(get_generated_image_service),
) -> List[GeneratedImageData]:
    return service.get_images_by_request_id(request_id, user_id)

@router.post("/report")
async def report_generated_images(
    image_ids: List[int],
    user_id: int = Depends(validate_user_token),
    service: GeneratedImageService = Depends(get_generated_image_service),
) -> None:
    return service.report_images(user_id, image_ids)

@router.post("/delete")
async def delete_generated_images(
    image_ids: List[int],
    user_id: int = Depends(validate_user_token),
    service: GeneratedImageService = Depends(get_generated_image_service),
) -> None:
    return service.delete_images(user_id, image_ids)