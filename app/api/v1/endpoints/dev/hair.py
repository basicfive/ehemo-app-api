from fastapi import APIRouter, status
from fastapi.params import Depends

from app.api.v1.dependencies.hair import get_gender_service, get_hair_style_service, get_length_service, \
    get_color_service, get_specific_color_service, get_hair_style_length_service, \
    get_hair_design_service, get_lora_model_service, get_hair_variant_model_service, get_publish_service, \
    get_hair_design_color_service
from app.schemas.hair.color import ColorCreate, ColorInDB, SpecificColorInDB, SpecificColorCreate
from app.schemas.hair.gender import GenderCreate, GenderInDB
from app.schemas.hair.hair_design import HairDesignInDB, HairDesignCreate
from app.schemas.hair.hair_design_color import HairDesignColorInDB, HairDesignColorCreate
from app.schemas.hair.hair_style import HairStyleInDB, HairStyleCreate
from app.schemas.hair.hair_style_length import HairStyleLengthInDB, HairStyleLengthCreate
from app.schemas.hair.hair_variant_model import HairVariantModelInDB, HairVariantModelCreate
from app.schemas.hair.length import LengthInDB, LengthCreate
from app.schemas.hair.lora_model import LoRAModelInDB, LoRAModelCreate
from app.services.hair import GenderService, HairStyleService, LengthService, ColorService, SpecificColorService, \
    HairStyleLengthService, HairDesignService, HairDesignColorService, LoRAModelService, HairVariantModelService
from app.services.publish import PublishService


router = APIRouter()
# api/v1/dev/hair-model

@router.post("/genders", response_model=GenderInDB, status_code=status.HTTP_201_CREATED)
def create_gender(
        gender: GenderCreate,
        service: GenderService = Depends(get_gender_service)
) -> GenderInDB:
    return service.create(obj_in=gender)

@router.post("/hairstyles", response_model=HairStyleInDB, status_code=status.HTTP_201_CREATED)
def create_hair_style(
        hair_style: HairStyleCreate,
        service: HairStyleService = Depends(get_hair_style_service)
) -> HairStyleInDB:
    return service.create(obj_in=hair_style)

@router.post("/lengths", response_model=LengthInDB, status_code=status.HTTP_201_CREATED)
def create_length(
        length: LengthCreate,
        service: LengthService = Depends(get_length_service)
) -> LengthInDB:
    return service.create(obj_in=length)

@router.post("/colors", response_model=ColorInDB, status_code=status.HTTP_201_CREATED)
def create_color(
        color: ColorCreate,
        service: ColorService = Depends(get_color_service)
) -> ColorInDB:
    return service.create(obj_in=color)

@router.post("/specific-colors", response_model=SpecificColorInDB, status_code=status.HTTP_201_CREATED)
def create_specific_color(
        specific_color: SpecificColorCreate,
        service: SpecificColorService = Depends(get_specific_color_service)
) -> SpecificColorInDB:
    return service.create(obj_in=specific_color)

@router.post("/lora-models", response_model=LoRAModelInDB, status_code=status.HTTP_201_CREATED)
def create_lora_model(
        lora_model: LoRAModelCreate,
        service: LoRAModelService = Depends(get_lora_model_service)
) -> LoRAModelInDB:
    return service.create(obj_in=lora_model)

@router.post("/hairstyle-lengths", response_model=HairStyleLengthInDB, status_code=status.HTTP_201_CREATED)
def create_hair_style_length(
        hair_style_length: HairStyleLengthCreate,
        service: HairStyleLengthService = Depends(get_hair_style_length_service)
) -> HairStyleLengthInDB:
    return service.create(obj_in=hair_style_length)

@router.post("/hair-designs", response_model=HairDesignInDB, status_code=status.HTTP_201_CREATED)
def create_hair_design(
        hair_design: HairDesignCreate,
        service: HairDesignService = Depends(get_hair_design_service)
) -> HairDesignInDB:
    return service.create(obj_in=hair_design)

@router.post("/hair-design-colors", response_model=HairDesignColorInDB, status_code=status.HTTP_201_CREATED)
def create_hair_design_color(
        hair_design_color: HairDesignColorCreate,
        service: HairDesignColorService = Depends(get_hair_design_color_service)
) -> HairDesignColorInDB:
    return service.create(obj_in=hair_design_color)

@router.post("/hair-variant-models", response_model=HairVariantModelInDB, status_code=status.HTTP_201_CREATED)
def create_hair_variant_model(
        hair_variant_model : HairVariantModelCreate,
        service: HairVariantModelService = Depends(get_hair_variant_model_service)
) -> HairVariantModelInDB:
    return service.create(obj_in=hair_variant_model)


@router.post("/publish", status_code=status.HTTP_200_OK)
def hair_model_option_publish(
        service: PublishService = Depends(get_publish_service)
):
    service.publish()
