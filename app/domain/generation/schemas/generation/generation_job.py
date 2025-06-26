from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.domain.generation.enums.generation_status import GenerationJobStatus


class GenerationJobCreate(BaseModel):
    expires_at: datetime

    image_count: int

    prompt: str

    is_user_hair_style: bool
    lora_model_s3_key: str
    lora_model_name: str

    distilled_cfg_scale: float
    width: int
    height: int

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_denoise_strength: Optional[float] = None

    generation_request_id: int


class GenerationJobUpdate(BaseModel):
    status: Optional[GenerationJobStatus] = None

    expires_at: Optional[datetime] = None


class GenerationJobInDB(BaseModel):
    id: int
    status: GenerationJobStatus

    expires_at: datetime

    image_count: int
    prompt: str
    is_user_hair_style: bool
    lora_model_s3_key: Optional[str] = None # nullable for backwards compatibility
    lora_model_name: Optional[str] = None # nullable for backwards compatibility

    distilled_cfg_scale: float
    width: int
    height: int

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_denoise_strength: Optional[float] = None

    generation_request_id: int

    class Config:
        from_attributes=True