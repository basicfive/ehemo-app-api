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

class ImageResolutionUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    width: Optional[int]
    height: Optional[int]
    aspect_width: Optional[int]
    aspect_height: Optional[int]
    image_s3_key: Optional[str]

class ImageResolutionInDB(BaseModel):
    id: int
    title: str
    description: str
    width: int
    height: int
    aspect_width: int
    aspect_height: int
    image_s3_key: str

    class Config:
        from_attributes=True