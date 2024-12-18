from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app import timezone_settings


class UserCreate(BaseModel):
    email: str
    provider: str
    social_id: str
    timezone: str = timezone_settings.SEOUL

class UserUpdate(BaseModel):
    fcm_token: Optional[str] = None

    email: Optional[str] = None
    provider: Optional[str] = None
    social_id: Optional[str] = None

    deleted: Optional[bool] = None
    timezone: Optional[str] = None

class UserInDB(BaseModel):
    id: int
    uuid: str
    fcm_token: str

    email: str
    provider: str
    social_id: str

    deleted: bool
    timezone: str

    class Config:
        from_attributes=True