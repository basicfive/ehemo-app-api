from pydantic import BaseModel

from app.core.enums.generation_status import GenerationResultEnum


class FCMGenerationResultData(BaseModel):
    generation_status: GenerationResultEnum
