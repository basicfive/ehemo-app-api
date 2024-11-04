from typing import Optional
from pydantic import BaseModel

class GeneratedImageGroupCreate(BaseModel):
    user_id: int
    generation_request_id: int
    thumbnail_image_s3_key: str
    rating: int = 0
    title: str

class GeneratedImageGroupUpdate(BaseModel):
    user_id: Optional[int] = None
    generation_request_id: Optional[int] = None
    thumbnail_image_s3_key: Optional[str] = None
    rating: Optional[int] = None
    title: Optional[str] = None

class GeneratedImageGroupInDB(BaseModel):
    id:int
    user_id: int
    generation_request_id: int
    thumbnail_image_s3_key: str
    rating: int
    title: str

    class Config:
        from_attributes=True