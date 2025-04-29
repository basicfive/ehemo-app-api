from pydantic import BaseModel
from typing import List

class HairStyleOption(BaseModel):
    is_user_hair_style: bool

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

