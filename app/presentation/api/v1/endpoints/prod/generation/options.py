from typing import List
from fastapi import APIRouter, Depends

from app.application.generation.options.dto.generation_options import HairStyleOption, PromptComponentOption, ImageRatioOption
from app.application.generation.options.generation_options_service import GenerationOptionsService, get_generation_options_service
from app.application.user.auth import validate_user_token

router = APIRouter()

@router.get("/hair-options")
def get_hair_options(
    user_id: int = Depends(validate_user_token),
    service: GenerationOptionsService = Depends(get_generation_options_service)
) -> List[HairStyleOption]:
    return service.get_hair_style_options(user_id)

@router.get("/prompt-component-options")
def get_prompt_component_options(
    _: int = Depends(validate_user_token),
    service: GenerationOptionsService = Depends(get_generation_options_service)
) -> List[PromptComponentOption]:
    return service.get_prompt_component_options()

@router.get("/image-ratio-options")
def get_image_ratio_options(
    _: int = Depends(validate_user_token),
    service: GenerationOptionsService = Depends(get_generation_options_service)
) -> List[ImageRatioOption]:
    return service.get_image_ratio_options()

