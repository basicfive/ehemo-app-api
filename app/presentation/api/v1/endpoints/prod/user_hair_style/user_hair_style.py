from fastapi import APIRouter, Depends

from app.application.user_hair_style.training.dto.request_training import UserHairStyleRegisterRequest, UserHairStyleRegisterResponse
from app.application.user_hair_style.training.request_training_service import RequestTrainingService, get_request_training_service
from app.application.user_hair_style.query.user_hair_style_query_service import UserHairStyleQueryService, get_user_hair_style_query_service
from app.application.user.auth import validate_user_token
from typing import List
from app.application.user_hair_style.query.dto.query import UserHairStyleInfo, UserHairStyleDetail

router = APIRouter()

@router.post("/register")
def request_training(
    request: UserHairStyleRegisterRequest,
    service: RequestTrainingService = Depends(get_request_training_service)
) -> UserHairStyleRegisterResponse:
    return service.request_training(request)

@router.get("/all/info")
def get_all_user_hair_styles(
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> List[UserHairStyleInfo]:
    return service.get_all_user_hair_style_infos(user_id)

@router.get("/{user_hair_style_id}/info")
def get_user_hair_style_info(
    user_hair_style_id: int,
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> UserHairStyleInfo:
    return service.get_user_hair_style_info(user_hair_style_id)

@router.get("/{user_hair_style_id}/detail")
def get_user_hair_style_detail(
    user_hair_style_id: int,
    user_id: int = Depends(validate_user_token),
    service: UserHairStyleQueryService = Depends(get_user_hair_style_query_service)
) -> UserHairStyleDetail:
    return service.get_user_hair_style_detail(user_hair_style_id)
