from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi import Form

from app.application.services.user.dto.auth import TokenResponse
from app.application.services.user.user_auth import UserAuthApplicationService, \
    get_google_user_auth_application_service, get_kakao_user_auth_application_service, \
    get_apple_user_auth_application_service

router = APIRouter()

# /api/v1/dev/user/auth

@router.get("/auth/google-web-login-url", response_model=str, status_code=status.HTTP_200_OK)
def get_google_web_login_url(
        service: UserAuthApplicationService = Depends(get_google_user_auth_application_service)
) -> str:
    return service.get_web_login_url()

@router.get("/auth/google-web-callback", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def google_web_callback(
        code: str,
        service: UserAuthApplicationService = Depends(get_google_user_auth_application_service)
) -> TokenResponse:
    return service.web_auth_callback(code=code)

@router.get("/auth/kakao-web-login-url", response_model=str, status_code=status.HTTP_200_OK)
def get_kakao_web_login_url(
        service: UserAuthApplicationService = Depends(get_kakao_user_auth_application_service)
) -> str:
    return service.get_web_login_url()

@router.get("/auth/kakao-web-callback", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def get_kakao_web_callback(
        code: str,
        service: UserAuthApplicationService = Depends(get_kakao_user_auth_application_service)
) -> TokenResponse:
    return service.web_auth_callback(code=code)

@router.get("/auth/apple-web-login-url", response_model=str, status_code=status.HTTP_200_OK)
def get_apple_web_login_url(
        service: UserAuthApplicationService = Depends(get_apple_user_auth_application_service)
) -> str:
    return service.get_web_login_url()

@router.post("/auth/apple-web-callback", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def get_apple_web_callback(
        code: str = Form(...),
        id_token: str = Form(...),
        state: str = Form(...),
        service: UserAuthApplicationService = Depends(get_apple_user_auth_application_service)
) -> TokenResponse:
    return service.web_auth_callback(code=code)
