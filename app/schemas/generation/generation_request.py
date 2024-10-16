
from pydantic import BaseModel
from typing_extensions import Optional

from app.schemas.hair.gender import GenderInDB
from app.schemas.hair.hair_style import HairStyleInDB
from app.schemas.hair.length import LengthInDB
from app.schemas.hair.color import ColorInDB
from app.schemas.scene.background import BackgroundInDB
from app.schemas.scene.image_resolution import ImageResolutionInDB
from app.schemas.user.user import UserInDB

# TODO: DTO가 여기 있는게 맞나..
class GenerationRequestCreateRequest(BaseModel):
    user_id: int
    gender_id: int
    hair_style_id: int
    length_id: int
    color_id: int
    background_id: int
    image_resolution_id: int

class GenerationRequestCreateResponse(BaseModel):
    generation_request_id: int
    user: UserInDB
    gender: GenderInDB
    hair_style: HairStyleInDB
    length: Optional[LengthInDB]
    color: ColorInDB
    background: BackgroundInDB
    image_resolution: ImageResolutionInDB

class GenerationRequestCreate(BaseModel):
    user_id: int
    hair_variant_model_id: int
    background_id: int
    image_resolution_id: int

class GenerationRequestUpdate(BaseModel):
    user_id: Optional[int]
    hair_variant_model_id: Optional[int]
    background_id: Optional[int]
    image_resolution_id: Optional[int]

class GenerationRequestInDB(BaseModel):
    id: int
    user_id: int
    hair_variant_model_id: int
    background_id: int
    image_resolution_id: int

    class Config:
        from_attributes=True