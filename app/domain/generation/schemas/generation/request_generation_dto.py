from pydantic import BaseModel
from typing import Optional

class RequestGenerationDto(BaseModel):
    is_user_hair_model: bool
    hair_style_id: Optional[int]
    user_hair_style_id: Optional[int]
    image_ratio_id: int
    is_high_res: bool
