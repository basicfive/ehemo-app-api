from typing import List
from fastapi import APIRouter, Depends, status
from app.api.v1.endpoints.prod.generation.dto import HairStyleOptionRequest, HairStyleLengthOptionRequest, HairDesignColorOptionRequest
from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_design_color import HairDesignColorInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.hair_style_length import HairStyleLengthInDB
from app.application.services.hair_model.hair_model_option import HairOptionApplicationService, \
    get_hair_option_application_service

router = APIRouter()

#/api/v1/prod/generation/
@router.get("/gender-options", response_model=List[GenderInDB], status_code=status.HTTP_200_OK)
def get_gender_options(
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[GenderInDB]:
    return service.get_gender_options()

@router.get("/hairstyle-options", response_model=List[HairStyleInDB], status_code=status.HTTP_200_OK)
def get_hair_style_options(
        request: HairStyleOptionRequest,
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[HairStyleInDB]:
    return service.get_hair_style_options(gender_id=request.gender_id)

@router.get("/hairstyle-length-options", response_model=List[HairStyleLengthInDB], status_code=status.HTTP_200_OK)
def get_hair_style_length_options(
        request: HairStyleLengthOptionRequest,
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[HairStyleLengthInDB]:
    return service.get_hair_style_length_options(request.hair_style_id)

@router.get("/hair-design-color-options", response_model=List[HairDesignColorInDB], status_code=status.HTTP_200_OK)
def get_hair_design_color_options(
        request: HairDesignColorOptionRequest,
        service: HairOptionApplicationService = Depends(get_hair_option_application_service)
) -> List[HairDesignColorInDB]:
    return service.get_hair_design_color_options(hair_style_id=request.hair_style_id, length_id=request.length_id)
