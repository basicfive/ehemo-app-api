from typing import Optional
from pydantic import BaseModel

class LengthCreate(BaseModel):
    title: str
    description: str
    prompt: str
    order: int

class LengthUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    prompt: Optional[str]
    order: Optional[int]

class LengthInDB(BaseModel):
    id: int
    title: str
    description: str
    prompt: str
    order: int

    class Config:
        from_attributes=True