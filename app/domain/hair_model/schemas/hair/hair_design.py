from typing import Optional
from pydantic import BaseModel

class HairDesignCreate(BaseModel):
    hair_style_id: int
    length_id: Optional[int]

class HairDesignUpdate(BaseModel):
    hair_style_id: Optional[int]
    length_id: Optional[int]

class HairDesignInDB(BaseModel):
    id: int
    hair_style_id: int
    length_id: Optional[int]

    class Config:
        from_attributes=True
