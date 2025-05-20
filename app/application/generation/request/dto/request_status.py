from pydantic import BaseModel
from datetime import datetime

from app.domain.generation.enums.generation_status import GenerationRequestResult

class RequestStatus(BaseModel):
    generation_request_id: int
    result: GenerationRequestResult
    expires_at: datetime

    
