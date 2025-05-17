from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class GeneratedImageData(BaseModel):
    id: int
    image_url: str
    s3_key: str
    generation_request_id: Optional[int] = None
    created_at: datetime
    width: int
    height: int
