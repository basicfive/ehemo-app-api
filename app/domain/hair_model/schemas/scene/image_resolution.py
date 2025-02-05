from typing import Optional

from pydantic import BaseModel

class ImageResolutionCreate(BaseModel):
    title: str
    description: str
    width: int
    height: int
    aspect_width: int
    aspect_height: int
    image_s3_key: str
    order: int
    is_upscale: int

    image_ratio_id: int

class ImageResolutionUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    width: Optional[int]
    height: Optional[int]
    aspect_width: Optional[int]
    aspect_height: Optional[int]
    image_s3_key: Optional[str]
    order: Optional[int]
    is_upscale: Optional[bool]

    image_ratio_id: Optional[int]

class ImageResolutionInDB(BaseModel):
    id: int
    title: str
    description: str
    width: int
    height: int
    aspect_width: int
    aspect_height: int
    image_s3_key: str
    order: int
    is_upscale: bool
    image_ratio_id: int

    class Config:
        from_attributes=True