from typing import Optional
from pydantic import BaseModel

from app.domain.common.enums.gender import Gender

class HairStyleCreate(BaseModel):
    order: int
    gender: Gender
    thumbnail_s3_key: str
    title: str
    description: str
    hair_style_lora_id: int

class HairStyleUpdate(BaseModel):
    order: Optional[int] = None

class HairStyleInDB(BaseModel):
    id: int
    order: int
    gender: Gender
    thumbnail_s3_key: str
    title: str
    description: str
    hair_style_lora_id: int

    class Config:
        from_attributes = True