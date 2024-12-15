from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.base import get_db
from app.domain.versioning.models.app_version import AppVersion
from app.domain.versioning.models.enums.app_version import PlatformEnum
from app.domain.versioning.schemas.app_version import AppVersionCreate, AppVersionUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository


class AppVersionRepository(CRUDRepository[AppVersion, AppVersionCreate, AppVersionUpdate]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=AppVersion)

    def get_by_platform(self, platform: PlatformEnum):
        stmt = select(AppVersion).where(AppVersion.platform == platform)
        return self.db.execute(stmt).scalar_one()

def get_app_version_repository(db: Session = Depends(get_db)):
    return AppVersionRepository(db=db)