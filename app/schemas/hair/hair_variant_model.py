from typing import Optional
from pydantic import BaseModel

class HairVariantModelCreate(BaseModel):
    hair_design_color_id: int
    lora_model_id: int

class HairVariantModelUpdate(BaseModel):
    hair_design_color_id: Optional[int]
    lora_model_id: Optional[int]

class HairVariantModelInDB(BaseModel):
    id: int
    hair_design_color_id: int
    lora_model_id: int

    class Config:
        from_attributes=True

