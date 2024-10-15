from typing import Optional

from pydantic import BaseModel

class BackgroundCreate(BaseModel):
    title: str
    description: str
    prompt: str
    image_s3_key: str

class BackgroundUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    prompt: Optional[str]
    image_s3_key: Optional[str]

class BackgroundInDB(BaseModel):
    id: int
    title: str
    description: str
    prompt: str
    image_s3_key: str

    class Config:
        from_attributes=True
