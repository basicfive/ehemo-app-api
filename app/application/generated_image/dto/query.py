from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class GeneratedImageData(BaseModel):
    id: int
    image_url: str
    last_modified_image_url: Optional[str]
    is_custom_background: bool
    generated_image_group_id: int
    width: int
    height: int

class GeneratedImageGroupData(BaseModel):
    id: int
    generation_request_id: int
    thumbnail_image_url: str
    title: str
    created_at: datetime

