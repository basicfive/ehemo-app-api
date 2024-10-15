from typing import Optional
from pydantic import BaseModel

class HairStyleLengthCreate(BaseModel):
    image_s3_key: str
    hair_style_id: int
    length_id: int

class HairStyleLengthUpdate(BaseModel):
    image_s3_key: Optional[str]
    hair_style_id: Optional[int]
    length_id: Optional[int]

class HairStyleLengthInDB(BaseModel):
    id: int
    image_s3_key: str
    hair_style_id: int
    length_id: int

    class Config:
        from_attributes=True
