from pydantic import BaseModel
from typing import List
from app.domain.common.enums.gender import Gender

class UserHairStyleRegisterRequest(BaseModel):
    gender: Gender
    title: str
    description: str
    uploaded_image_s3_keys: List[str]
    length_prompt: str

class UserHairStyleRegisterResponse(BaseModel):
    estimated_time_sec: int