from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.domain.common.enums.gender import Gender

from app.domain.generation.dto.request_generation import PromptComponentAnswer
from app.domain.generation.enums.generation_status import GenerationRequestResult

from app.application.generation.options.dto.generation_options import HairStyleOption, PromptComponentOption, ImageRatioOption

class GenerationRequestStatus(BaseModel):
    generation_status: GenerationRequestResult
    remaining_sec: int

class GenerationRequestInfo(BaseModel):
    generation_request_id: int
    user_id: int

    request_number: str
    generation_result: GenerationRequestResult
    created_at: datetime

    remaining_sec: int

    selected_hair_style_option: HairStyleOption
    selected_prompt_component_answer: List[PromptComponentAnswer]
    selected_image_ratio_option: ImageRatioOption

    is_user_reference_image: bool
    user_reference_image_s3_key: str
    user_reference_image_thumbnail_url: str

    consumed_token: int