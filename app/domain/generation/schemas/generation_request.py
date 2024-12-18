
from pydantic import BaseModel
from typing_extensions import Optional

from app.domain.generation.models.enums.generation_status import GenerationResultEnum


class GenerationRequestInDB(BaseModel):
    id: int
    user_id: int
    hair_variant_model_id: int
    background_id: int
    image_resolution_id: int
    generation_result: GenerationResultEnum

    class Config:
        from_attributes=True

class GenerationRequestCreate(BaseModel):
    user_id: int
    hair_variant_model_id: int
    background_id: int
    image_resolution_id: int

class GenerationRequestUpdate(BaseModel):
    hair_variant_model_id: Optional[int] = None
    background_id: Optional[int] = None
    image_resolution_id: Optional[int] = None
    generation_result: Optional[GenerationResultEnum] = None


