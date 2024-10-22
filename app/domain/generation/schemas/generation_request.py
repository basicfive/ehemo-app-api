
from pydantic import BaseModel
from typing_extensions import Optional



class GenerationRequestCreate(BaseModel):
    user_id: int
    hair_variant_model_id: int
    background_id: int
    image_resolution_id: int

class GenerationRequestUpdate(BaseModel):
    user_id: Optional[int]
    hair_variant_model_id: Optional[int]
    background_id: Optional[int]
    image_resolution_id: Optional[int]

class GenerationRequestInDB(BaseModel):
    id: int
    user_id: int
    hair_variant_model_id: int
    background_id: int
    image_resolution_id: int

    class Config:
        from_attributes=True