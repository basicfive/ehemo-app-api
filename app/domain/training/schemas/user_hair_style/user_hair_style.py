from pydantic import BaseModel
from typing import Optional
from app.domain.common.enums.gender import Gender

class UserHairStyleCreate(BaseModel):
    user_id: int
    gender: Gender
    thumbnail_s3_key: str
    title: str
    description: str
    user_hair_style_lora_id: int

class UserHairStyleUpdate(BaseModel):
    thumbnail_s3_key: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

class UserHairStyleInDB(BaseModel):
    id: int
    user_id: int
    gender: Gender
    thumbnail_s3_key: str
    title: str
    description: str
    user_hair_style_lora_id: int

    class Config:
        from_attributes = True