from typing import Optional

from pydantic import BaseModel

class BackgroundCreate(BaseModel):
    title: str
    description: str
    prompt: str
    image_s3_key: str
    order: int

class BackgroundUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    prompt: Optional[str]
    image_s3_key: Optional[str]
    order: Optional[int]

class BackgroundInDB(BaseModel):
    id: int
    title: str
    description: str
    prompt: str
    image_s3_key: str
    order: int

    class Config:
        from_attributes=True
