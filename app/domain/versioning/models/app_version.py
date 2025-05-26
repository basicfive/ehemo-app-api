from sqlalchemy import Column, String, Enum, Boolean

from app.domain.time_stamp_model import TimeStampModel
from app.domain.versioning.models.enums.app_version import PlatformEnum

class AppVersion(TimeStampModel):
    __tablename__="app_version"
    platform = Column(Enum(PlatformEnum), nullable=False)
    version = Column(String, nullable=False)
    is_minimum_version = Column(Boolean, nullable=False)
    is_latest_version = Column(Boolean, nullable=False)
