from typing import Optional, List
from app.domain.hair_model.models.hair import Gender, HairStyle, Length, Color, SpecificColor, LoRAModel
from app.domain.hair_model.models.scene import Background, ImageResolution

"""
각 orm 모델 타입을 필드로 갖고 있어 BaseModel을 (정상적으로) 사용하기 어려움
"""

class HairModelDetails:
    def __init__(
            self,
            gender: Gender,
            hair_style: HairStyle,
            length: Optional[Length],
            color: Color,
            specific_color_list: List[SpecificColor],
            lora_model: LoRAModel,
            background: Background,
            image_resolution: ImageResolution,
    ):
        self.gender=gender
        self.hair_style=hair_style
        self.length=length
        self.color=color
        self.specific_color_list=specific_color_list
        self.lora_model=lora_model
        self.background=background
        self.image_resolution=image_resolution
