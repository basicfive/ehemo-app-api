from typing import Optional
from pydantic import BaseModel

class CreateGenerationRequestRequest(BaseModel):
    gender_id: int
    hair_style_id: int
    length_id: Optional[int]
    color_id: int
    background_id: int
    image_resolution_id: int

class UpdateGenerationRequestRequest(BaseModel):
    gender_id: int
    hair_style_id: int
    length_id: Optional[int]
    color_id: int
    background_id: int
    image_resolution_id: int

class GenerationRequestResponse(BaseModel):
    generation_request_id: int
    remaining_sec: int
    generated_image_cnt_per_request: int
