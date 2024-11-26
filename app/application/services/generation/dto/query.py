from typing import Optional
from pydantic import BaseModel

from app.core.enums.generation_status import GenerationResultEnum

class GenerationRequestStatusResponse(BaseModel):
    generation_status: GenerationResultEnum
    remaining_sec: int
    generated_image_group_id: Optional[int] = None
