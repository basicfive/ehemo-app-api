from typing import Optional
from pydantic import BaseModel

from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB
from app.domain.user.schemas.user import UserInDB

class CreateGenerationRequestRequest(BaseModel):
    user_id: int
    gender_id: int
    hair_style_id: int
    length_id: Optional[int]
    color_id: int
    background_id: int
    image_resolution_id: int

class CreateGenerationRequestResponse(BaseModel):
    generation_request_id: int
    user: UserInDB
    gender: GenderInDB
    hair_style: HairStyleInDB
    length: Optional[LengthInDB]
    color: ColorInDB
    background: BackgroundInDB
    image_resolution: ImageResolutionInDB
