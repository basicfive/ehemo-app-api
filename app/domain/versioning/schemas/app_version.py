from typing import Optional
from pydantic import BaseModel

from app.domain.versioning.models.enums.app_version import PlatformEnum


class AppVersionCreate(BaseModel):
    platform: PlatformEnum
    min_version: str
    latest_version: str
    store_url: str

class AppVersionUpdate(BaseModel):
    platform: Optional[PlatformEnum] = None
    min_version: Optional[str] = None
    latest_version: Optional[str] = None
    store_url: Optional[str] = None

class AppVersionInDB(BaseModel):
    id: int
    platform: PlatformEnum
    min_version: str
    latest_version: str
    store_url: str

    class Config:
        from_attributes=True
