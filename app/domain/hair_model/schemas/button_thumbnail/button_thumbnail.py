from typing import Optional
from pydantic import BaseModel

class ModelThumbnailCreate(BaseModel):
    s3_key: str
    gender_id: int

class ModelThumbnailUpdate(BaseModel):
    s3_key: Optional[str] = None
    gender_id: Optional[int] = None

class ModelThumbnailInDB(BaseModel):
    id: int
    s3_key: str
    gender_id: int

    class Config:
        from_attributes=True
