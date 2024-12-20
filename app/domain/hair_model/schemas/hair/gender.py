from typing import Optional
from pydantic import BaseModel

class GenderCreate(BaseModel):
    title: str
    description: str
    image_s3_key: str
    order: int
    prompt: str

class GenderUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    image_s3_key: Optional[str]
    order: Optional[int]
    prompt: Optional[str]

class GenderInDB(BaseModel):
    id: int
    title: str
    description: str
    image_s3_key: str
    order: int
    prompt: str

    class Config:
        from_attributes=True
