from fastapi import Depends

from app.core.config import versioning_settings
from app.application.versioning.dto.app_version import CheckVersionResponse
from app.domain.versioning.models.app_version import AppVersion
from app.domain.versioning.models.enums.app_version import PlatformEnum
from app.domain.versioning.services.app_version import suggests_update, requires_update
from app.infrastructure.repositories.versioning.versioning import AppVersionRepository, get_app_version_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository
from app.domain.user.models.user import User

class AppVersionQueryApplicationService:
    def __init__(
            self,
            app_version_repo: AppVersionRepository,
            user_repo: UserRepository,
    ):
        self.app_version_repo = app_version_repo
        self.user_repo = user_repo

    def is_user_signed_up_before_update(self, current_version: str, user_id: int, platform: PlatformEnum) -> bool:
        user: User = self.user_repo.get(user_id)

        app_version: AppVersion = self.app_version_repo.get_version_by_platform_and_version_number(platform=platform, version=current_version)
        return (user.created_at < app_version.created_at)

    # TODO: version 입력 형식 validation
    def check_version(self, current_version: str, platform: PlatformEnum) -> CheckVersionResponse:
        latest_app_version: AppVersion = self.app_version_repo.get_latest_by_platform(platform=platform)
        minimum_app_version: AppVersion = self.app_version_repo.get_minimum_by_platform(platform=platform)
        store_url = versioning_settings.APP_VERSION_IOS_STORE_URL if platform == PlatformEnum.IOS else versioning_settings.APP_VERSION_ANDROID_STORE_URL

        return CheckVersionResponse(
            requires_update=requires_update(current_version, minimum_app_version.version),
            suggests_update=suggests_update(current_version, latest_app_version.version),
            store_url=store_url,
        )

def get_app_version_query_application_service(
        app_version_repo: AppVersionRepository = Depends(get_app_version_repository),
        user_repo: UserRepository = Depends(get_user_repository),
) -> AppVersionQueryApplicationService:
    return AppVersionQueryApplicationService(
        app_version_repo=app_version_repo,
        user_repo=user_repo,
    )