from fastapi import APIRouter, status
from fastapi.params import Depends

from app.application.services.user.dto.auth import TokenResponse
from app.application.services.user.user_auth import UserAuthApplicationService, get_google_user_auth_application_service

router = APIRouter()

# /prod/user/
@router.post("auth/google-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def google_login(
        token: str,
        service: UserAuthApplicationService = Depends(get_google_user_auth_application_service)
) -> TokenResponse:
    return service.mobile_login(id_token=token)

# @router.post("/kakao-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
# def google_login(
#         token: str,
#         service: UserAuthApplicationService = Depends()
# ) -> TokenResponse:
#     return service.social_login(id_token=token)
#
# @router.post("/apple-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
# def google_login(
#         token: str,
#         service: UserAuthApplicationService = Depends()
# ) -> TokenResponse:
#     return service.social_login(id_token=token)

@router.post("auth/logout", response_model=bool, status_code=status.HTTP_200_OK)
def logout(
        refresh_token: str,
        service: UserAuthApplicationService = Depends(get_google_user_auth_application_service)
) -> bool:
    return service.logout(refresh_token)

@router.post("auth/refresh_tokens", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh_tokens(
        refresh_token: str,
        service: UserAuthApplicationService = Depends(get_google_user_auth_application_service)
) -> TokenResponse:
    return service.refresh_tokens(refresh_token)