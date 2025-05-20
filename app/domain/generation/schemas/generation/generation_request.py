
from pydantic import BaseModel
from datetime import datetime
from typing_extensions import Optional

from app.domain.generation.enums.generation_status import GenerationRequestResult


class GenerationRequestCreate(BaseModel):
    user_id: int

    request_number: str

    is_user_hair_style: bool
    hair_style_id: Optional[int] = None
    user_hair_style_id: Optional[int] = None
    
    image_resolution_id: int

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_denoise_strength: Optional[float] = None

    final_generation_prompt: str
    consumed_tokens: int


class GenerationRequestUpdate(BaseModel):
    result: Optional[GenerationRequestResult] = None
    is_favorite: Optional[bool] = None


class GenerationRequestInDB(BaseModel):
    id: int
    request_number: str
    result: GenerationRequestResult
    user_id: int

    is_user_hair_style: bool
    hair_style_id: Optional[int] = None
    user_hair_style_id: Optional[int] = None

    image_resolution_id: int

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_denoise_strength: Optional[float] = None

    final_generation_prompt: str
    consumed_tokens: int

    is_favorite: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True

