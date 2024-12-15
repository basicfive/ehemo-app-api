from sqlalchemy import Column, String, Enum

from app.core.db.time_stamp_model import TimeStampModel
from app.domain.versioning.models.enums.app_version import PlatformEnum


class AppVersion(TimeStampModel):
    __tablename__="app_version"
    platform = Column(Enum(PlatformEnum), nullable=False)
    min_version = Column(String, nullable=False)
    latest_version = Column(String, nullable=False)
    store_url = Column(String, nullable=False)

