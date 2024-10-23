from typing import Optional
from pydantic import BaseModel

class GeneratedImageGroupCreate(BaseModel):
    user_id: int
    generation_request_id: int
    thumbnail_image_s3_key: str

class GeneratedImageGroupUpdate(BaseModel):
    user_id: Optional[int]
    generation_request_id: Optional[int]
    thumbnail_image_s3_key: Optional[str]

class GeneratedImageGroupInDB(BaseModel):
    id:int
    user_id: int
    generation_request_id: int
    thumbnail_image_s3_key: str

    class Config:
        from_attributes=True