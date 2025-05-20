from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.domain.common.enums.gender import Gender

from app.domain.generation.dto.request_generation import PromptComponentAnswer
from app.domain.generation.enums.generation_status import GenerationRequestResult

from app.application.generation.options.dto.generation_options import HairStyleOption, PromptComponentOption, ImageRatioOption

class GenerationRequestInfoPreview(BaseModel):
    generation_request_id: int

    thumbnail_url: str

    created_at: datetime
    result: GenerationRequestResult

    hair_style_name: str
    selected_options: str

    is_favorite: bool

class GenerationRequestInfo(BaseModel):
    generation_request_id: int

    request_number: str
    result: GenerationRequestResult
    created_at: datetime

    is_favorite: bool

    remaining_sec: int

    selected_hair_style_option: HairStyleOption
    selected_prompt_component_answer: List[PromptComponentAnswer]
    selected_image_ratio_option: ImageRatioOption

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_url: Optional[str] = None
    user_reference_image_denoise_strength: Optional[float] = None

    consumed_tokens: int