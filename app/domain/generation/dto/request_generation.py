from pydantic import BaseModel
from typing import List, Optional

from app.domain.generation.enums.reference_image_similarity import ReferenceImageSimilarity

class PromptComponentAnswer(BaseModel):
    prompt_component_question_id: int
    prompt_component_question_title: str
    is_random: bool
    is_not_selected: bool
    answer: str

class RequestGenerationDto(BaseModel):
    is_user_hair_style: bool
    hair_style_id: Optional[int] = None
    user_hair_style_id: Optional[int] = None

    is_high_res: bool
    image_ratio_id: int

    is_user_reference_image: bool
    user_reference_image_s3_key: Optional[str] = None
    user_reference_image_similarity: Optional[ReferenceImageSimilarity] = None

    prompt_component_answers: List[PromptComponentAnswer]