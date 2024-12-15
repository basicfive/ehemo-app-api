from fastapi import APIRouter, Depends, status

from app.application.services.user.auth import validate_user_token
from app.application.services.versioning.app_version import AppVersionQueryApplicationService, \
    get_app_version_query_application_service
from app.application.services.versioning.dto.app_version import CheckVersionResponse
from app.domain.versioning.models.enums.app_version import PlatformEnum

router = APIRouter()

#/prod/versioning

@router.get("/check/{platform}", response_model=CheckVersionResponse, status_code=status.HTTP_200_OK)
def check_version(
        current_version: str,
        platform: PlatformEnum,
        _: int = Depends(validate_user_token),
        service: AppVersionQueryApplicationService = Depends(get_app_version_query_application_service),
) -> CheckVersionResponse:
    return service.check_version(current_version, platform)