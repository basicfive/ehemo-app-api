from typing import Optional
from pydantic import BaseModel

class HairDesignColorCreate(BaseModel):
    image_s3_key: str
    hair_design_id: int
    color_id: int

class HairDesignColorUpdate(BaseModel):
    image_s3_key: Optional[str]
    hair_design_id: Optional[int]
    color_id: Optional[int]

class HairDesignColorInDB(BaseModel):
    id: int
    image_s3_key: str
    hair_design_id: int
    color_id: int

    class Config:
        from_attributes=True
