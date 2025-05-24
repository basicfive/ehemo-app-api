from fastapi import APIRouter, Depends
from typing import List

from app.application.user_hair_style.training.dto.request_training import UserHairStyleRegisterRequest, UserHairStyleRegisterResponse
from app.application.user_hair_style.training.request_training_service import RequestTrainingService, get_request_training_service
from app.application.user_hair_style.query.user_hair_style_query_service import UserHairStyleQueryService, get_user_hair_style_query_service
from app.application.user.auth import validate_user_token
from app.application.user_hair_style.training.naming_suggestion_service import NamingSuggestionService, get_naming_suggestion_service
from app.application.user_hair_style.training.dto.suggestion import NamingSuggestions
from app.application.user_hair_style.query.dto.query import UserHairStyleInfo, UserHairStyleDetail
from app.application.generation.request.dto.request import ImageUploadUrlDto

router = APIRouter()

@router.get("/naming-suggestions")
def get_naming_suggestion(
    _: int = Depends(validate_user_token),
    service: NamingSuggestionService = Depends(get_naming_suggestion_service)
) -> NamingSuggestions:
    return service.get_naming_suggestion()

@router.get("/image-upload-urls")
def get_image_upload_urls(
    image_cnt: int,
    _: int = Depends(validate_user_token),
    service: RequestTrainingService = Depends(get_request_training_service)
) -> List[ImageUploadUrlDto]:
    return service.get_upload_urls_for_training_images(image_cnt=image_cnt)

@router.post("/register")
async def request_training(
    request: UserHairStyleRegisterRequest,
    user_id: int = Depends(validate_user_token),
    service: RequestTrainingService = Depends(get_request_training_service)
) -> UserHairStyleRegisterResponse:
    return await service.request_training(request, user_id)

@router.get("/all/info")
def get_all_user_hair_styles(
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> List[UserHairStyleInfo]:
    return service.get_all_user_hair_style_infos(user_id)

@router.get("/{user_hair_style_id}/info")
def get_user_hair_style_info(
    user_hair_style_id: int,
    _: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> UserHairStyleInfo:
    return service.get_user_hair_style_info(user_hair_style_id)

@router.get("/{user_hair_style_id}/detail")
def get_user_hair_style_detail(
    user_hair_style_id: int,
    _: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> UserHairStyleDetail:
    return service.get_user_hair_style_detail(user_hair_style_id)
