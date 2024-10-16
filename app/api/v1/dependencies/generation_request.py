from fastapi import Depends

from app.api.v1.dependencies.generation import get_generation_request_service
from app.api.v1.dependencies.hair import get_hair_variant_model_service, get_gender_service, get_hair_style_service, \
    get_length_service, get_color_service, get_hair_design_color_service, get_hair_design_service, \
    get_hair_style_length_service
from app.api.v1.dependencies.scene import get_background_service, get_image_resolution_service
from app.api.v1.dependencies.user import get_user_service
from app.usecase.generation_request import GenerationRequestUseCase, SelectOptionUseCase

# TODO: usecase와 service의 의존성 주입 함수를 같은 패키지에 두려다보니 파일명이 애매하다.

def get_generation_request_usecase(
        hair_variant_model_service: Depends(get_hair_variant_model_service),
        generation_request_service: Depends(get_generation_request_service),
        user_service: Depends(get_user_service),
        gender_service: Depends(get_gender_service),
        hair_style_service: Depends(get_hair_style_service),
        length_service: Depends(get_length_service),
        color_service: Depends(get_color_service),
        background_service: Depends(get_background_service),
        image_resolution_service: Depends(get_image_resolution_service),
        hair_design_color_service: Depends(get_hair_design_color_service),
        hair_design_service: Depends(get_hair_design_service),
) -> GenerationRequestUseCase:
    return GenerationRequestUseCase(
        hair_variant_model_service=hair_variant_model_service,
        generation_request_service=generation_request_service,
        user_service=user_service,
        gender_service=gender_service,
        hair_style_service=hair_style_service,
        length_service=length_service,
        color_service=color_service,
        background_service=background_service,
        image_resolution_service=image_resolution_service,
        hair_design_color_service=hair_design_color_service,
        hair_design_service=hair_design_service
    )

def get_select_option_usecase(
        gender_service=Depends(get_gender_service),
        hair_style_service=Depends(get_hair_style_service),
        length_service=Depends(get_length_service),
        hair_style_length_service=Depends(get_hair_style_length_service),
        hair_design_service=Depends(get_hair_design_service),
        hair_design_color_service=Depends(get_hair_design_color_service),
        background_service=Depends(get_background_service),
        image_resolution_service=Depends(get_image_resolution_service)
) -> SelectOptionUseCase:
    return SelectOptionUseCase(
        gender_service=gender_service,
        hair_style_service=hair_style_service,
        length_service=length_service,
        hair_style_length_service=hair_style_length_service,
        hair_design_service=hair_design_service,
        hair_design_color_service=hair_design_color_service,
        background_service=background_service,
        image_resolution_service=image_resolution_service
    )