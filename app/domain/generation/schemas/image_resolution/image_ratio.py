from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImageRatioCreate(BaseModel):
    title: str
    description: str
    aspect_width: int
    aspect_height: int
    image_s3_key: str
    order: int

class ImageRatioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    aspect_width: Optional[int] = None
    aspect_height: Optional[int] = None
    image_s3_key: Optional[str] = None
    order: Optional[int] = None

class ImageRatioInDB(BaseModel):
    id: int
    title: str
    description: str
    aspect_width: int
    aspect_height: int
    image_s3_key: str
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True