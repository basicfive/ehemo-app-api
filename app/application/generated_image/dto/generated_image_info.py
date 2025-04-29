from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.domain.generation.enums.generated_image_status import GeneratedImageStatus

class GeneratedImageData(BaseModel):
    id: int
    status: GeneratedImageStatus
    image_url: str
    s3_key: str
    generation_job_id: int
    created_at: datetime