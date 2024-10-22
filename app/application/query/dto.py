from typing import Optional, List
from pydantic import BaseModel
from app.domain.hair_model.models.hair import Gender, HairStyle, Length, Color, SpecificColor, LoRAModel
from app.domain.hair_model.models.scene import Background, ImageResolution

"""
BaseModel 이기 때문에 typing 제대로 할거면 BaseModel 의존하는 schema 의존하도록 하는게 맞는데...
일단 이 dto 는 특수한 경우라 보류
"""

class HairModelDetails(BaseModel):
    gender: Gender
    hair_style: HairStyle
    length: Optional[Length]
    color: Color
    specific_color_list: List[SpecificColor]
    lora_model: LoRAModel
    background: Background
    image_resolution: ImageResolution

    class Config:
        arbitrary_types_allowed=True
        from_attributes=True