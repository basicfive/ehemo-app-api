from fastapi import APIRouter, Depends
from typing import List

from app.application.services.hair_model.dto.model_thumbnail import ModelThumbnailData
from app.application.services.hair_model.model_thumbnail import ModelThumbnailQueryService, \
    get_model_thumbnail_query_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# /prod/home/model_thumbnail

@router.get("/model_thumbnail/all")
def get_all_button_thumbnail_images(
        _: int = Depends(validate_user_token),
        service: ModelThumbnailQueryService = Depends(get_model_thumbnail_query_service)
) -> List[ModelThumbnailData]:
    return service.get_all_button_thumbnail_images()
