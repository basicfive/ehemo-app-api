from pydantic import BaseModel
from typing import List

from app.domain.common.enums.gender import Gender

class HairStyleOption(BaseModel):
    is_user_hair_style: bool
    gender: Gender

    id: int
    title: str
    description: str
    thumbnail_url: str

class PromptComponentOption(BaseModel):
    question_id: int
    title: str
    question: str
    suggestions: List[str]

class ImageRatioOption(BaseModel):
    id: int
    title: str
    description: str
    thumbnail_url: str
    aspect_width: int
    aspect_height: int

class ReferenceImageUploadUrlResponse(BaseModel):
    upload_url: str
    s3_key: str
