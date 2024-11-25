from pydantic import BaseModel

from app.core.enums.generation_status import GenerationResultEnum

class GenerationRequestStatusResponse(BaseModel):
    generation_status: GenerationResultEnum
    remaining_sec: int
