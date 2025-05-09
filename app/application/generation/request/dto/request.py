from typing import List, Optional
from typing import Optional
from pydantic import BaseModel

from app.domain.generation.enums.prompt_component import PromptComponentType
from app.domain.generation.dto.request_generation import RequestGenerationDto


class PromptComponentQuestionResponse(BaseModel):
    id: int
    component_type: PromptComponentType
    question: str
    suggestions: List[str]


class ReferenceImageUploadUrlResponse(BaseModel):
    upload_url: str
    s3_key: str

# 제대로 사용하려면 필드 값 모두 가져와야함.
class GenerationRequestRequest(RequestGenerationDto):

    pass


class GenerationRequestResponse(BaseModel):
    generation_request_id: int
    remaining_sec: int

