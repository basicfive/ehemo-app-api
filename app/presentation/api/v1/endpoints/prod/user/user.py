from fastapi import APIRouter, Depends, status

from app.application.user.auth import validate_user_token
from app.application.user.dto.user_info import UserInfoResponse
from app.application.user.user import UserApplicationService, get_user_application_service

router = APIRouter()

# /prod/user/
@router.get("/info", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
def get_user_info(
        user_id: int = Depends(validate_user_token),
        service: UserApplicationService = Depends(get_user_application_service)
) -> UserInfoResponse:
    return service.get_user_info(user_id=user_id)

@router.put("/info/with-fcm", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
def update_fcm_and_get_user_info(
        fcm_token: str,
        user_id: int = Depends(validate_user_token),
        service: UserApplicationService = Depends(get_user_application_service)
) -> UserInfoResponse:
    return service.update_fcm_token(fcm_token=fcm_token, user_id=user_id)

@router.patch("/soft-delete", status_code=status.HTTP_200_OK)
def soft_delete_user(
        user_id: int = Depends(validate_user_token),
        service: UserApplicationService = Depends(get_user_application_service)
):
    service.soft_delete_user(user_id)
