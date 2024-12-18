from typing import Dict
from pydantic import BaseModel

from app.domain.generation.models.enums.generation_status import GenerationResultEnum

class FCMGenerationResultData(BaseModel):
    generation_status: GenerationResultEnum

    def to_fcm_data(self) -> Dict[str, str]:
        return {
            field_name: str(getattr(self, field_name).value)
            for field_name in self.model_fields
        }