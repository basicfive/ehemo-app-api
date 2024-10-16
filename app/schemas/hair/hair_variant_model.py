from typing import Optional
from pydantic import BaseModel

class HairVariantModelCreate(BaseModel):
    gender_id: int
    hair_style_id: int
    length_id: Optional[int]
    color_id: int
    lora_model_id: int

class HairVariantModelUpdate(BaseModel):
    gender_id: Optional[int]
    hair_style_id: Optional[int]
    length_id: Optional[int]
    color_id: Optional[int]
    lora_model_id: Optional[int]

class HairVariantModelInDB(BaseModel):
    id: int
    gender_id: int
    hair_style_id: int
    length_id: Optional[int]
    color_id: int
    lora_model_id: int

    class Config:
        from_attributes=True

