from typing import Optional
from pydantic import BaseModel

from app.domain.versioning.models.enums.app_version import PlatformEnum


class AppVersionCreate(BaseModel):
    platform: PlatformEnum
    version: str
    is_minimum_version: bool
    is_latest_version: bool

class AppVersionUpdate(BaseModel):
    platform: Optional[PlatformEnum] = None
    version: Optional[str] = None
    is_minimum_version: Optional[bool] = None
    is_latest_version: Optional[bool] = None

class AppVersionInDB(BaseModel):
    id: int
    platform: PlatformEnum
    version: str
    is_minimum_version: bool
    is_latest_version: bool

    class Config:
        from_attributes=True
