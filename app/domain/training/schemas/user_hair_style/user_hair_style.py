from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.domain.common.enums.gender import Gender
from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus

class UserHairStyleCreate(BaseModel):
    user_id: int
    gender: Gender
    thumbnail_s3_key: str
    title: str
    description: str
    order: int

class UserHairStyleUpdate(BaseModel):
    status: Optional[UserHairStyleStatus] = None
    title: Optional[str] = None
    description: Optional[str] = None
    user_hair_style_lora_id: Optional[int] = None

class UserHairStyleInDB(BaseModel):
    id: int
    status: UserHairStyleStatus
    user_id: int
    gender: Gender
    thumbnail_s3_key: str
    title: str
    description: str
    user_hair_style_lora_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True