from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.hair import HairDesignRepository, HairDesignColorRepository, ColorRepository, GenderRepository, \
    HairStyleRepository, LengthRepository, SpecificColorRepository, LoRAModelRepository, HairStyleLengthRepository, \
    HairVariantModelRepository
from app.services.hair import HairDesignColorService, GenderService, LengthService, ColorService, SpecificColorService, \
    LoRAModelService, HairStyleService, HairStyleLengthService, HairDesignService, HairVariantModelService
from app.services.publish import PublishService


def get_gender_repository(db: Session = Depends(get_db)) -> GenderRepository:
    return GenderRepository(db=db)

def get_hair_style_repository(db: Session = Depends(get_db)) -> HairStyleRepository:
    return HairStyleRepository(db=db)

def get_length_repository(db: Session = Depends(get_db)) -> LengthRepository:
    return LengthRepository(db=db)

def get_color_repository(db: Session = Depends(get_db)) -> ColorRepository:
    return ColorRepository(db=db)

def get_specific_color_repository(db: Session = Depends(get_db)) -> SpecificColorRepository:
    return SpecificColorRepository(db=db)

def get_lora_model_repository(db: Session = Depends(get_db)) -> LoRAModelRepository:
    return LoRAModelRepository(db=db)

def get_hair_style_length_repository(db: Session = Depends(get_db)) -> HairStyleLengthRepository:
    return HairStyleLengthRepository(db=db)

def get_hair_design_repository(db: Session = Depends(get_db)) -> HairDesignRepository:
    return HairDesignRepository(db=db)

def get_hair_design_color_repository(db: Session = Depends(get_db)) -> HairDesignColorRepository:
    return HairDesignColorRepository(db=db)

def get_hair_variant_model_repository(db: Session = Depends(get_db)) -> HairVariantModelRepository:
    return HairVariantModelRepository(db=db)

def get_gender_service(repo: GenderRepository = Depends(get_gender_repository)) -> GenderService:
    return GenderService(repo=repo)

def get_length_service(repo: LengthRepository = Depends(get_length_repository)) -> LengthService:
    return LengthService(repo=repo)

def get_color_service(repo: ColorRepository = Depends(get_color_repository)) -> ColorService:
    return ColorService(repo=repo)

def get_lora_model_service(repo: LoRAModelRepository = Depends(get_lora_model_repository)) -> LoRAModelService:
    return LoRAModelService(repo=repo)

def get_specific_color_service(repo: SpecificColorRepository = Depends(get_specific_color_repository)) -> SpecificColorService:
    return SpecificColorService(repo=repo)

def get_hair_style_service(repo: HairStyleRepository = Depends(get_hair_style_repository)) -> HairStyleService:
    return HairStyleService(repo=repo)

def get_hair_style_length_service(
        repo: HairStyleLengthRepository = Depends(get_hair_style_length_repository)
) -> HairStyleLengthService:
    return HairStyleLengthService(repo=repo)

def get_hair_design_service(
        repo: HairDesignRepository = Depends(get_hair_design_repository)
) -> HairDesignService:
    return HairDesignService(repo=repo)

def get_hair_design_color_service(
        repo: HairDesignColorRepository = Depends(get_hair_design_color_repository),
) -> HairDesignColorService:
    return HairDesignColorService(repo=repo)

def get_hair_variant_model_service(
        repo: HairVariantModelRepository = Depends(get_hair_variant_model_repository),
) -> HairVariantModelService:
    return HairVariantModelService(repo=repo)

def get_publish_service(
        gender_repo: GenderRepository = Depends(get_gender_repository),
        hair_style_repo: HairStyleRepository = Depends(get_hair_style_repository),
        length_repo: LengthRepository = Depends(get_length_repository),
        hair_style_length_repo: HairStyleLengthRepository = Depends(get_hair_style_length_repository),
        hair_design_repo: HairDesignRepository = Depends(get_hair_design_repository),
        hair_design_color_repo: HairDesignColorRepository = Depends(get_hair_design_color_repository),
        hair_variant_model_repo: HairVariantModelRepository = Depends(get_hair_variant_model_repository)
) -> PublishService:
    return PublishService(
        gender_repo=gender_repo,
        hair_style_repo=hair_style_repo,
        length_repo=length_repo,
        hair_style_length_repo=hair_style_length_repo,
        hair_design_repo=hair_design_repo,
        hair_design_color_repo=hair_design_color_repo,
        hair_variant_model_repo=hair_variant_model_repo
    )
