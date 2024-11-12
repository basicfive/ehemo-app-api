from pydantic import BaseModel
from datetime import datetime

class GeneratedImageData(BaseModel):
    image_url: str
    generated_image_group_id: int

class GeneratedImageGroupData(BaseModel):
    id: int
    generation_request_id: int
    thumbnail_image_url: str
    title: str
    created_at: datetime

