from typing import Optional, List
from pydantic import BaseModel

from app.core.enums.inference_types import InferenceType

class ImageInfo(BaseModel):
    generated_image_id: int
    s3_key: str

class GenerationConsumeMessage(BaseModel):
    is_success: bool
    image_info_list: List[ImageInfo]

class GenerationPublishMessage(BaseModel):
    image_info_list: List[ImageInfo]
    time_to_live_sec: int

    image_count: int

    prompt: str
    is_user_hair_style: bool
    user_hair_lora_model_s3_key: Optional[str] = None
    hair_lora_model_name: str

    distilled_cfg_scale: float
    width: int
    height: int

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_denoise_strength: Optional[float] = None

class NormalGenerationPublishMessage(GenerationPublishMessage):
    inference_type: InferenceType = InferenceType.NORMAL
    generation_job_id: int
class NormalGenerationConsumeMessage(GenerationConsumeMessage):
    inference_type: InferenceType = InferenceType.NORMAL
    generation_job_id: int
