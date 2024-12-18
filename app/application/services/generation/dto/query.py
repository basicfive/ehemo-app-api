from typing import Optional
from pydantic import BaseModel

from app.domain.generation.models.enums.generation_status import GenerationResultEnum

from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB


class GenerationRequestStatusResponse(BaseModel):
    generation_status: GenerationResultEnum
    remaining_sec: int
    generated_image_group_id: Optional[int] = None

class GenerationRequestDetails(BaseModel):
    generation_request_id: int
    gender: GenderInDB
    hair_style: HairStyleInDB
    length: Optional[LengthInDB]
    color: ColorInDB
    background: BackgroundInDB
    image_resolution: ImageResolutionInDB

class GenerationRequestStatusWithDetails(BaseModel):
    generation_request_id: Optional[int] = None
    gender: Optional[GenderInDB] = None
    hair_style: Optional[HairStyleInDB] = None
    length: Optional[LengthInDB] = None
    color: Optional[ColorInDB] = None
    background: Optional[BackgroundInDB] = None
    image_resolution: Optional[ImageResolutionInDB] = None

    generation_status: Optional[GenerationResultEnum] = None
    remaining_sec: Optional[int] = None
    generated_image_group_id: Optional[int] = None
