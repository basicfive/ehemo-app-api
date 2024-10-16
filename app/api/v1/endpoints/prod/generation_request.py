from typing import List
from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies.generation_request import get_select_option_usecase, get_generation_request_usecase
from app.api.v1.dto.generation_request import HairStyleOptionRequest, HairStyleLengthOptionRequest, HairDesignColorOptionRequest
from app.schemas.generation.generation_request import GenerationRequestCreateRequest, GenerationRequestCreateResponse
from app.schemas.hair.gender import GenderInDB
from app.schemas.hair.hair_design_color import HairDesignColorInDB
from app.schemas.hair.hair_style import HairStyleInDB
from app.schemas.hair.hair_style_length import HairStyleLengthInDB
from app.usecase.generation_request import SelectOptionUseCase, GenerationRequestUseCase

router = APIRouter()

#/generation/
@router.get("/gender-options", response_model=List[GenderInDB], status_code=status.HTTP_200_OK)
def get_gender_options(
        service: SelectOptionUseCase = Depends(get_select_option_usecase)
) -> List[GenderInDB]:
    return service.get_gender_options()

@router.get("/hairstyle-options", response_model=List[HairStyleInDB], status_code=status.HTTP_200_OK)
def get_hair_style_options(
        request: HairStyleOptionRequest,
        service: SelectOptionUseCase = Depends(get_select_option_usecase)
) -> List[HairStyleInDB]:
    return service.get_hair_style_options(gender_id=request.gender_id)

@router.get("/hairstyle-length-options", response_model=List[HairStyleLengthInDB], status_code=status.HTTP_200_OK)
def get_hair_style_length_options(
        request: HairStyleLengthOptionRequest,
        service: SelectOptionUseCase = Depends(get_select_option_usecase)
) -> List[HairStyleLengthInDB]:
    return service.get_hair_style_length_options(request.hair_style_id)

@router.get("/hair-design-color-options", response_model=List[HairDesignColorInDB], status_code=status.HTTP_200_OK)
def get_hair_design_color_options(
        request: HairDesignColorOptionRequest,
        service: SelectOptionUseCase = Depends(get_select_option_usecase)
) -> List[HairDesignColorInDB]:
    return service.get_hair_design_color_options(hair_style_id=request.hair_style_id, length_id=request.length_id)

@router.post("/request", response_model=GenerationRequestCreateResponse, status_code=status.HTTP_200_OK)
def create_generation_request(
        generation_request: GenerationRequestCreateRequest,
        service: GenerationRequestUseCase = Depends(get_generation_request_usecase)
) -> GenerationRequestCreateResponse:
    return service.create_generation_request(request=generation_request)
