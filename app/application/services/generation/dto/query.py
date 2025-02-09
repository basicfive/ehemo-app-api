from typing import Optional
from pydantic import BaseModel

from app.domain import ImageRatio
from app.domain.generation.models.enums.generation_status import GenerationResultEnum

from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_ratio import ImageRatioInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB


class GenerationRequestStatus(BaseModel):
    generation_status: GenerationResultEnum
    remaining_sec: int
    result_confirmed: bool
    generated_image_group_id: Optional[int] = None

class GenerationRequestDetails(BaseModel):
    generation_request_id: int
    generated_image_cnt_per_request: int
    gender: GenderInDB
    hair_style: HairStyleInDB
    length: Optional[LengthInDB]
    color: ColorInDB
    background: BackgroundInDB
    image_ratio: ImageRatioInDB
    image_resolution: ImageResolutionInDB

# Optional 붙어있는 이유는 가장 마지막 생성 값이 없는 유저의 경우 None으로 반환
class GenerationRequestStatusWithDetails(BaseModel):
    status: Optional[GenerationRequestStatus] = None
    details: Optional[GenerationRequestDetails] = None