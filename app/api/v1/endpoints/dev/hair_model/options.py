from fastapi import APIRouter, status, Depends
from typing import List
from app.domain.hair_model.schemas.hair.color import ColorCreate, ColorInDB, SpecificColorInDB, SpecificColorCreate
from app.domain.hair_model.schemas.hair.gender import GenderCreate, GenderInDB
from app.domain.hair_model.schemas.hair.hair_design import HairDesignInDB, HairDesignCreate
from app.domain.hair_model.schemas.hair.hair_design_color import HairDesignColorInDB, HairDesignColorCreate
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB, HairStyleCreate
from app.domain.hair_model.schemas.hair.hair_style_length import HairStyleLengthInDB, HairStyleLengthCreate
from app.domain.hair_model.schemas.hair.hair_variant_model import HairVariantModelInDB, HairVariantModelCreate
from app.domain.hair_model.schemas.hair.length import LengthInDB, LengthCreate
from app.domain.hair_model.schemas.hair.lora_model import LoRAModelInDB, LoRAModelCreate
from app.application.services.hair_model.crud import GenderCRUDService, HairStyleCRUDService, \
    LengthCRUDService, ColorCRUDService, SpecificColorCRUDService, \
    HairStyleLengthCRUDService, HairDesignCRUDService, HairDesignColorCRUDService, LoRAModelCRUDService, \
    HairVariantModelCRUDService, get_gender_crud_service, get_hair_style_crud_service, get_length_crud_service, \
    get_color_crud_service, get_specific_color_crud_service, get_lora_model_crud_service, \
    get_hair_style_length_crud_service, get_hair_design_crud_service, get_hair_design_color_crud_service, \
    get_hair_variant_model_crud_service, get_background_crud_service, get_posture_and_clothing_crud_service, \
    get_image_resolution_crud_service
from app.domain.hair_model.schemas.scene.background import BackgroundInDB, BackgroundCreate
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB, ImageResolutionCreate
from app.domain.hair_model.schemas.scene.posture_and_clothing import PostureAndClothingInDB, PostureAndClothingCreate
from app.application.services.hair_model.crud import BackgroundCRUDService, PostureAndClothingCRUDService, ImageResolutionCRUDService

router = APIRouter()
# api/v1/dev/hair-model

@router.post("/genders", response_model=GenderInDB, status_code=status.HTTP_201_CREATED)
async def create_gender(
        gender: GenderCreate,
        service: GenderCRUDService = Depends(get_gender_crud_service)
) -> GenderInDB:
    return await service.create(obj_in=gender)

@router.post("/hairstyles", response_model=HairStyleInDB, status_code=status.HTTP_201_CREATED)
async def create_hair_style(
        hair_style: HairStyleCreate,
        service: HairStyleCRUDService = Depends(get_hair_style_crud_service)
) -> HairStyleInDB:
    return await service.create(obj_in=hair_style)

@router.post("/lengths", response_model=LengthInDB, status_code=status.HTTP_201_CREATED)
async def create_length(
        length: LengthCreate,
        service: LengthCRUDService = Depends(get_length_crud_service)
) -> LengthInDB:
    return await service.create(obj_in=length)

@router.post("/colors", response_model=ColorInDB, status_code=status.HTTP_201_CREATED)
async def create_color(
        color: ColorCreate,
        service: ColorCRUDService = Depends(get_color_crud_service)
) -> ColorInDB:
    return await service.create(obj_in=color)

@router.post("/specific-colors", response_model=SpecificColorInDB, status_code=status.HTTP_201_CREATED)
async def create_specific_color(
        specific_color: SpecificColorCreate,
        service: SpecificColorCRUDService = Depends(get_specific_color_crud_service)
) -> SpecificColorInDB:
    return await service.create(obj_in=specific_color)

@router.post("/lora-models", response_model=LoRAModelInDB, status_code=status.HTTP_201_CREATED)
async def create_lora_model(
        lora_model: LoRAModelCreate,
        service: LoRAModelCRUDService = Depends(get_lora_model_crud_service)
) -> LoRAModelInDB:
    return await service.create(obj_in=lora_model)

@router.post("/hairstyle-lengths", response_model=HairStyleLengthInDB, status_code=status.HTTP_201_CREATED)
async def create_hair_style_length(
        hair_style_length: HairStyleLengthCreate,
        service: HairStyleLengthCRUDService = Depends(get_hair_style_length_crud_service)
) -> HairStyleLengthInDB:
    return await service.create(obj_in=hair_style_length)

@router.post("/hair-designs", response_model=HairDesignInDB, status_code=status.HTTP_201_CREATED)
async def create_hair_design(
        hair_design: HairDesignCreate,
        service: HairDesignCRUDService = Depends(get_hair_design_crud_service)
) -> HairDesignInDB:
    return await service.create(obj_in=hair_design)

@router.post("/hair-design-colors", response_model=HairDesignColorInDB, status_code=status.HTTP_201_CREATED)
async def create_hair_design_color(
        hair_design_color: HairDesignColorCreate,
        service: HairDesignColorCRUDService = Depends(get_hair_design_color_crud_service)
) -> HairDesignColorInDB:
    return await service.create(obj_in=hair_design_color)

@router.post("/hair-variant-models", response_model=HairVariantModelInDB, status_code=status.HTTP_201_CREATED)
async def create_hair_variant_model(
        hair_variant_model : HairVariantModelCreate,
        service: HairVariantModelCRUDService = Depends(get_hair_variant_model_crud_service)
) -> HairVariantModelInDB:
    return await service.create(obj_in=hair_variant_model)

@router.post("/backgrounds", response_model=BackgroundInDB, status_code=status.HTTP_201_CREATED)
async def create_background(
        background: BackgroundCreate,
        service: BackgroundCRUDService = Depends(get_background_crud_service)
) -> BackgroundInDB:
    return await service.create(obj_in=background)

@router.post("/posture-and-clothing/batch", response_model=bool, status_code=status.HTTP_201_CREATED)
async def create_posture_and_clothing_batch(
        posture_and_clothing_list: List[PostureAndClothingCreate],
        service: PostureAndClothingCRUDService = Depends(get_posture_and_clothing_crud_service)
) -> bool:
    return await service.create_batch(posture_and_clothing_list)

@router.post("/image-resolution", response_model=ImageResolutionInDB, status_code=status.HTTP_201_CREATED)
async def create_image_resolution(
        image_resolution: ImageResolutionCreate,
        service: ImageResolutionCRUDService = Depends(get_image_resolution_crud_service)
) -> ImageResolutionInDB:
    return await service.create(obj_in=image_resolution)

