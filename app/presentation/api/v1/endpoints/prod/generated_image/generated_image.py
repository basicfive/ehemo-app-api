from fastapi import APIRouter, Depends

from app.application.generated_image.generated_image_info_service import get_generated_image_info_service
from app.application.generated_image.dto.generated_image_info import GeneratedImageData
from app.application.user.auth import validate_user_token
from typing import List
from app.application.generated_image.generated_image_info_service import GeneratedImageInfoService

router = APIRouter()

@router.get("/")
async def get_generated_image_info(
    user_id: int = Depends(validate_user_token),
    service: GeneratedImageInfoService = Depends(get_generated_image_info_service),
) -> List[GeneratedImageData]:
    return service.get_user_generated_images(user_id)
