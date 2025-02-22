from pydantic import BaseModel
from typing import Optional


class BackgroundForMattingCreate(BaseModel):
    image_s3_key: str
    image_resolution_id: int

class BackgroundForMattingUpdate(BaseModel):
    image_s3_key: Optional[str] = None
    image_resolution_id: Optional[int] = None

class BackgroundForMattingInDB(BaseModel):
    id: int
    image_s3_key: str
    image_resolution_id: int

    class Config:
        from_attributes=True
