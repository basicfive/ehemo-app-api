from fastapi import APIRouter, Depends
from typing import List, Optional

# from app.application.user_hair_style.training.dto.request_training import UserHairStyleRegisterRequest, UserHairStyleRegisterResponse
# from app.application.user_hair_style.training.request_training_service import RequestTrainingService, get_request_training_service
from app.application.user_hair_style.user_hair_style.user_hair_style_query_service import UserHairStyleQueryService, get_user_hair_style_query_service
from app.application.user.auth import validate_user_token
# from app.application.user_hair_style.training.naming_suggestion_service import NamingSuggestionService, get_naming_suggestion_service
# from app.application.user_hair_style.training.dto.suggestion import NamingSuggestions
from app.application.user_hair_style.user_hair_style.dto.query import UserHairStyleInfo, UserHairStyleDetail
from app.application.generation.request.dto.request import ImageUploadUrlDto
from app.application.user_hair_style.user_hair_style.dto.status import RegisterStatus
from app.application.user_hair_style.user_hair_style.user_hair_style_update_service import UserHairStyleUpdateService, get_user_hair_style_update_service

router = APIRouter()

# @router.get("/naming-suggestions")
# def get_naming_suggestion(
#     _: int = Depends(validate_user_token),
#     service: NamingSuggestionService = Depends(get_naming_suggestion_service)
# ) -> NamingSuggestions:
#     return service.get_naming_suggestion()

# @router.get("/image-upload-urls")
# def get_image_upload_urls(
#     image_cnt: int,
#     _: int = Depends(validate_user_token),
#     service: RequestTrainingService = Depends(get_request_training_service)
# ) -> List[ImageUploadUrlDto]:
#     return service.get_upload_urls_for_training_images(image_cnt=image_cnt)

# @router.post("/register")
# async def request_training(
#     request: UserHairStyleRegisterRequest,
#     user_id: int = Depends(validate_user_token),
#     service: RequestTrainingService = Depends(get_request_training_service)
# ) -> UserHairStyleRegisterResponse:
#     return await service.request_training(request, user_id)

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

@router.get("/pending")
def get_pending_user_hair_styles(
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> List[RegisterStatus]:
    return service.get_pending_user_hair_styles(user_id)

@router.get("/{user_hair_style_id}/status")
def get_user_hair_style_status(
    user_hair_style_id: int,
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> RegisterStatus:
    return service.get_user_hair_style_status(user_hair_style_id, user_id)

@router.post("/{user_hair_style_id}/delete")
def soft_delete_user_hair_style(
    user_hair_style_id: int,
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleUpdateService = Depends(get_user_hair_style_update_service)
) -> None:
    service.soft_delete_user_hair_style(user_hair_style_id, user_id)

@router.put("/{user_hair_style_id}/title-and-description")
def update_user_hair_style_title_and_description(
    user_hair_style_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleUpdateService = Depends(get_user_hair_style_update_service)
) -> None:
    service.update_user_hair_style_title_and_description(user_id, user_hair_style_id, title, description)