from fastapi import APIRouter, Depends

from app.application.user_hair_style.training.dto.request_training import UserHairStyleRegisterRequest, UserHairStyleRegisterResponse
from app.application.user_hair_style.training.request_training_service import RequestTrainingService, get_request_training_service

router = APIRouter()

@router.post("/training")
def request_training(
    request: UserHairStyleRegisterRequest,
    service: RequestTrainingService = Depends(get_request_training_service)
) -> UserHairStyleRegisterResponse:
    return service.request_training(request)
