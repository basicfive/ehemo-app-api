from pydantic import BaseModel
from datetime import datetime

class GeneratedImageData(BaseModel):
    id: int
    image_url: str
    s3_key: str
    generation_request_id: int
    created_at: datetime