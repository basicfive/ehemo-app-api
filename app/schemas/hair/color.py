from typing import Optional
from pydantic import BaseModel

class SpecificColorCreate(BaseModel):
    prompt: str
    color_id: int

class SpecificColorUpdate(BaseModel):
    prompt: Optional[str]
    color_id: Optional[int]

class SpecificColorInDB(BaseModel):
    id: int
    prompt: str
    color_id: int

    class Config:
        from_attributes=True

class ColorCreate(BaseModel):
    title: str
    description: str
    order: int

class ColorUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    order: Optional[int]

class ColorInDB(BaseModel):
    id: int
    title: str
    description: str
    order: int

    class Config:
        from_attributes=True
