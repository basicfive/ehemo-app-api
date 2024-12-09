from typing import Optional
from pydantic import BaseModel

class ExampleGeneratedImageGroupCreate(BaseModel):
    title: str
    thumbnail_image_s3_key: str

class ExampleGeneratedImageGroupUpdate(BaseModel):
    title: Optional[str] = None
    thumbnail_image_s3_key: Optional[str] = None
    rating: Optional[int] = None
    deleted: Optional[bool] = None

class ExampleGeneratedImageGroupInDB(BaseModel):
    title: str
    thumbnail_image_s3_key: str
    rating: Optional[int]
    deleted: bool

    class Config:
        from_attributes=True
