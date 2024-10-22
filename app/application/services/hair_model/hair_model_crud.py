from typing import List
from fastapi import Depends
from app.core.decorators import handle_not_found
from app.domain.hair_model.models.hair import HairStyle, Gender, Length, HairStyleLength, Color, SpecificColor, LoRAModel, \
    HairDesignColor, HairVariantModel, HairDesign
from app.infrastructure.repositories.hair_model.hair_model import GenderRepository, HairStyleRepository, \
    LengthRepository, HairStyleLengthRepository, \
    ColorRepository, SpecificColorRepository, LoRAModelRepository, HairDesignColorRepository, HairDesignRepository, \
    HairVariantModelRepository, get_gender_repository, get_color_repository, get_lora_model_repository, \
    get_specific_color_repository, get_hair_style_repository, get_hair_style_length_repository, \
    get_hair_design_repository, get_hair_design_color_repository, get_hair_variant_model_repository, \
    BackgroundRepository, PostureAndClothingRepository, ImageResolutionRepository, get_image_resolution_repository, \
    get_posture_and_clothing_repository, get_background_repository, get_length_repository
from app.domain.hair_model.schemas.hair.color import ColorCreate, ColorUpdate, ColorInDB, SpecificColorInDB, SpecificColorCreate, SpecificColorUpdate
from app.domain.hair_model.schemas.hair.gender import GenderCreate, GenderUpdate, GenderInDB
from app.domain.hair_model.schemas.hair.hair_design import HairDesignCreate, HairDesignInDB, HairDesignUpdate
from app.domain.hair_model.schemas.hair.hair_design_color import HairDesignColorCreate, HairDesignColorInDB, HairDesignColorUpdate
from app.domain.hair_model.schemas.hair.hair_style import HairStyleCreate, HairStyleUpdate, HairStyleInDB
from app.domain.hair_model.schemas.hair.hair_style_length import HairStyleLengthCreate, HairStyleLengthInDB, HairStyleLengthUpdate
from app.domain.hair_model.schemas.hair.hair_variant_model import HairVariantModelCreate, HairVariantModelUpdate, HairVariantModelInDB
from app.domain.hair_model.schemas.hair.length import LengthCreate, LengthInDB, LengthUpdate
from app.domain.hair_model.schemas.hair.lora_model import LoRAModelCreate, LoRAModelInDB, LoRAModelUpdate
from app.domain.hair_model.models.scene import Background, PostureAndClothing, ImageResolution
from app.domain.hair_model.schemas.scene.background import BackgroundInDB, BackgroundCreate
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB, ImageResolutionCreate, ImageResolutionUpdate
from app.domain.hair_model.schemas.scene.posture_and_clothing import PostureAndClothingInDB, PostureAndClothingCreate, PostureAndClothingUpdate
from app.application.services.base_service import CRUDService



class GenderCRUDService(CRUDService[Gender, GenderInDB, GenderCreate, GenderUpdate, GenderRepository]):
    def __init__(self, repo: GenderRepository):
        super().__init__(repo, GenderInDB)

def get_gender_crud_service(repo: GenderRepository = Depends(get_gender_repository)) -> GenderCRUDService:
    return GenderCRUDService(repo=repo)


class LengthCRUDService(CRUDService[Length, LengthInDB, LengthCreate, LengthUpdate, LengthRepository]):
    def __init__(self, repo: LengthRepository):
        super().__init__(repo, LengthInDB)

def get_length_crud_service(repo: LengthRepository = Depends(get_length_repository)) -> LengthCRUDService:
    return LengthCRUDService(repo=repo)


class ColorCRUDService(CRUDService[Color, ColorInDB, ColorCreate, ColorUpdate, ColorRepository]):
    def __init__(self, repo: ColorRepository):
        super().__init__(repo, ColorInDB)

def get_color_crud_service(repo: ColorRepository = Depends(get_color_repository)) -> ColorCRUDService:
    return ColorCRUDService(repo=repo)


class LoRAModelCRUDService(CRUDService[LoRAModel, LoRAModelInDB, LoRAModelCreate, LoRAModelUpdate, LoRAModelRepository]):
    def __init__(self, repo: LoRAModelRepository):
        super().__init__(repo, LoRAModelInDB)

def get_lora_model_crud_service(repo: LoRAModelRepository = Depends(get_lora_model_repository)) -> LoRAModelCRUDService:
    return LoRAModelCRUDService(repo=repo)


class SpecificColorCRUDService(CRUDService[SpecificColor, SpecificColorInDB, SpecificColorCreate, SpecificColorUpdate, SpecificColorRepository]):
    def __init__(self, repo: SpecificColorRepository):
        super().__init__(repo, SpecificColorInDB)

def get_specific_color_crud_service(
        repo: SpecificColorRepository = Depends(get_specific_color_repository)) -> SpecificColorCRUDService:
    return SpecificColorCRUDService(repo=repo)


class HairStyleCRUDService(CRUDService[HairStyle, HairStyleInDB, HairStyleCreate, HairStyleUpdate, HairStyleRepository]):
    def __init__(self, repo: HairStyleRepository):
        super().__init__(repo, HairStyleInDB)

    def get_all_by_gender(self, gender_id: int) -> List[HairStyleInDB]:
        db_hair_style_list: List[HairStyle] = self.repo.get_all_by_gender(gender_id)
        return [HairStyleInDB.model_validate(db_hair_style) for db_hair_style in db_hair_style_list]

def get_hair_style_crud_service(repo: HairStyleRepository = Depends(get_hair_style_repository)) -> HairStyleCRUDService:
    return HairStyleCRUDService(repo=repo)



class HairStyleLengthCRUDService(CRUDService[HairStyleLength, HairStyleLengthInDB, HairStyleLengthCreate, HairStyleLengthUpdate, HairStyleLengthRepository]):
    def __init__(self, repo: HairStyleLengthRepository):
        super().__init__(repo, HairStyleLengthInDB)

    def get_all_by_hair_style(self, hair_style_id: int) -> List[HairStyleLengthInDB]:
        return [
            HairStyleLengthInDB.model_validate(db_hair_style_length)
            for db_hair_style_length in self.repo.get_all_by_hair_style(hair_style_id)
        ]

    # def get_all_by_length(self, length_id: int) -> List[HairStyleLengthInDB]:
    #     return [
    #         HairStyleLengthInDB.model_validate(db_hair_style_length)
    #         for db_hair_style_length in self.repo.get_all_by_length(length_id)
    #     ]

def get_hair_style_length_crud_service(
        repo: HairStyleLengthRepository = Depends(get_hair_style_length_repository)
) -> HairStyleLengthCRUDService:
    return HairStyleLengthCRUDService(repo=repo)


class HairDesignCRUDService(CRUDService[HairDesign, HairDesignInDB, HairDesignCreate, HairDesignUpdate, HairDesignRepository]):
    def __init__(self, repo: HairDesignRepository):
        super().__init__(repo, HairDesignInDB)

    def get_all_by_hair_style(self, hair_style_id: int) -> List[HairDesignInDB]:
        return [
            HairDesignInDB.model_validate(db_hair_design)
            for db_hair_design in self.repo.get_all_by_hair_style(hair_style_id)
        ]

    def get_all_by_hair_style_and_length(self, hair_style_id: int, length_id: int):
        return [
            HairDesignInDB.model_validate(db_hair_design)
            for db_hair_design in self.repo.get_all_by_hair_style_and_length(hair_style_id=hair_style_id, length_id=length_id)
        ]

    # def get_all_by_length(self, length_id: int) -> List[HairDesignInDB]:
    #     return [
    #         HairDesignInDB.model_validate(db_hair_style_length)
    #         for db_hair_style_length in self.repo.get_all_by_length(length_id)
    #     ]

def get_hair_design_crud_service(
        repo: HairDesignRepository = Depends(get_hair_design_repository)
) -> HairDesignCRUDService:
    return HairDesignCRUDService(repo=repo)



class HairDesignColorCRUDService(CRUDService[HairDesignColor, HairDesignColorInDB, HairDesignColorCreate, HairDesignColorUpdate, HairDesignColorRepository]):
    def __init__(self, repo: HairDesignColorRepository):
        super().__init__(repo,HairDesignColorInDB)

    def get_all_by_hair_design(self, hair_design_id: int) -> List[HairDesignColorInDB]:
        return [
            HairDesignColorInDB.model_validate(db_hair_design_color)
            for db_hair_design_color in self.repo.get_all_by_hair_design(hair_design_id)
        ]

def get_hair_design_color_crud_service(
        repo: HairDesignColorRepository = Depends(get_hair_design_color_repository),
) -> HairDesignColorCRUDService:
    return HairDesignColorCRUDService(repo=repo)


class HairVariantModelCRUDService(CRUDService[HairVariantModel,HairVariantModelInDB, HairVariantModelCreate, HairVariantModelUpdate, HairVariantModelRepository]):
    def __init__(self, repo: HairVariantModelRepository):
        super().__init__(repo, HairVariantModelInDB)

    @handle_not_found
    def get_by_hair_style_length_color(self, hair_style_id: int, length_id: int, color_id: int) -> HairVariantModelInDB:
        db_hair_variant_model: HairVariantModel = self.repo.get_by_hair_style_length_color(
            hair_style_id=hair_style_id,
            length_id=length_id,
            color_id=color_id
        )
        return HairVariantModelInDB.model_validate(db_hair_variant_model)

def get_hair_variant_model_crud_service(
        repo: HairVariantModelRepository = Depends(get_hair_variant_model_repository),
) -> HairVariantModelCRUDService:
    return HairVariantModelCRUDService(repo=repo)


class BackgroundCRUDService(CRUDService[Background, BackgroundInDB, BackgroundCreate, BackgroundCreate, BackgroundRepository]):
    def __init__(self, repo: BackgroundRepository):
        super().__init__(repo=repo, model_in_db=BackgroundInDB)

def get_background_crud_service(repo: BackgroundRepository = Depends(get_background_repository)) -> BackgroundCRUDService:
    return BackgroundCRUDService(repo=repo)


class PostureAndClothingCRUDService(
    CRUDService[PostureAndClothing, PostureAndClothingInDB, PostureAndClothingCreate, PostureAndClothingUpdate, PostureAndClothingRepository]
):
    def __init__(self, repo: PostureAndClothingRepository):
        super().__init__(repo=repo, model_in_db=PostureAndClothingInDB)

def get_posture_and_clothing_crud_service(repo: PostureAndClothingRepository = Depends(get_posture_and_clothing_repository)) -> PostureAndClothingCRUDService:
    return PostureAndClothingCRUDService(repo=repo)


class ImageResolutionCRUDService(
    CRUDService[ImageResolution, ImageResolutionInDB, ImageResolutionCreate, ImageResolutionUpdate, ImageResolutionRepository]
):
    def __init__(self, repo: ImageResolutionRepository):
        super().__init__(repo=repo, model_in_db=ImageResolutionInDB)

def get_image_resolution_crud_service(repo: ImageResolutionRepository = Depends(get_image_resolution_repository)) -> ImageResolutionCRUDService:
    return ImageResolutionCRUDService(repo=repo)
