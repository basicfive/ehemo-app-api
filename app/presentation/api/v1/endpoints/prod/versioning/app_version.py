from fastapi import APIRouter, Depends, status

from app.application.versioning.app_version import AppVersionQueryApplicationService, \
    get_app_version_query_application_service
from app.application.versioning.dto.app_version import CheckVersionResponse
from app.domain.versioning.models.enums.app_version import PlatformEnum
from app.application.user.auth import validate_user_token

router = APIRouter()

#/prod/versioning

@router.get("/is-user-signed-up-before-update/{platform}", response_model=bool, status_code=status.HTTP_200_OK)
def is_user_signed_up_before_update(
        current_version: str,
        platform: PlatformEnum,
        user_id: int = Depends(validate_user_token),
        service: AppVersionQueryApplicationService = Depends(get_app_version_query_application_service),
) -> bool:
    return service.is_user_signed_up_before_update(current_version, user_id, platform)

@router.get("/check/{platform}", response_model=CheckVersionResponse, status_code=status.HTTP_200_OK)
def check_version(
        current_version: str,
        platform: PlatformEnum,
        service: AppVersionQueryApplicationService = Depends(get_app_version_query_application_service),
) -> CheckVersionResponse:
    return service.check_version(current_version, platform)