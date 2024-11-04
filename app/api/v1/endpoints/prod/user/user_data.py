from fastapi import APIRouter, Depends, status

from app.application.services.user.auth import validate_user_token
from app.application.services.user.dto.user_data import UserTokenResponse
from app.application.services.user.user_data import UserDataApplicationService, get_user_data_application_service

router = APIRouter()

# /prod/user/

@router.get("/token", response_model=UserTokenResponse, status_code=status.HTTP_200_OK)
def get_user_token(
        user_id: int = Depends(validate_user_token),
        service: UserDataApplicationService = Depends(get_user_data_application_service)
) -> UserTokenResponse:
    return service.get_user_token(user_id=user_id)