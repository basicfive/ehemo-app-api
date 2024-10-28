from typing import List, Optional
from fastapi import APIRouter, Depends, status
from app.application.services.hair_model.dto.hair_model_option import GenderOption, HairStyleOption, \
    HairStyleLengthOption, HairDesignColorOption
from app.application.services.hair_model.hair_model_option import HairOptionApplicationService, \
    get_hair_option_application_service

router = APIRouter()

#/api/v1/prod/generation/

@router.get("/gender-options", response_model=List[GenderOption], status_code=status.HTTP_200_OK)
def get_gender_options(
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[GenderOption]:
    return service.get_gender_options()

@router.get("/hairstyle-options", response_model=List[HairStyleOption], status_code=status.HTTP_200_OK)
def get_hair_style_options(
        gender_id: int,
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[HairStyleOption]:
    return service.get_hair_style_options(gender_id=gender_id)

@router.get("/hairstyle-length-options", response_model=List[HairStyleLengthOption], status_code=status.HTTP_200_OK)
def get_hair_style_length_options(
        hair_style_id: int,
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[HairStyleLengthOption]:
    return service.get_hair_style_length_options(hair_style_id)

@router.get("/hair-design-color-options", response_model=List[HairDesignColorOption], status_code=status.HTTP_200_OK)
def get_hair_design_color_options(
        hair_style_id: int,
        length_id: Optional[int] = None,
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[HairDesignColorOption]:
    return service.get_hair_design_color_options(hair_style_id=hair_style_id, length_id=length_id)
