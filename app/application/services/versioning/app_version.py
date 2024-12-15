from fastapi import Depends

from app.application.services.versioning.dto.app_version import CheckVersionRequest, CheckVersionResponse
from app.domain.versioning.models.app_version import AppVersion
from app.domain.versioning.models.enums.app_version import PlatformEnum
from app.domain.versioning.services.app_version import suggests_update, requires_update
from app.infrastructure.repositories.versioning.app_version import AppVersionRepository, get_app_version_repository


class AppVersionQueryApplicationService:
    def __init__(
            self,
            app_version_repo: AppVersionRepository,
    ):
        self.app_version_repo = app_version_repo

    # TODO: version 입력 형식 validation
    def check_version(self, current_version: str, platform: PlatformEnum):
        app_version: AppVersion = self.app_version_repo.get_by_platform(platform=platform)
        return CheckVersionResponse(
            requires_update=requires_update(current_version, app_version.min_version),
            suggests_update=suggests_update(current_version, app_version.min_version),
            store_url=app_version.store_url,
        )

def get_app_version_query_application_service(
        app_version_repo: AppVersionRepository = Depends(get_app_version_repository),
) -> AppVersionQueryApplicationService:
    return AppVersionQueryApplicationService(
        app_version_repo=app_version_repo,
    )