from typing import List

from app.core.decorators import handle_not_found
from app.models.hair import HairStyle, Gender, Length, HairStyleLength, Color, SpecificColor, LoRAModel, \
    HairDesignColor, HairVariantModel, HairDesign
from app.repositories.hair import GenderRepository, HairStyleRepository, LengthRepository, HairStyleLengthRepository, \
    ColorRepository, SpecificColorRepository, LoRAModelRepository, HairDesignColorRepository, HairDesignRepository, \
    HairVariantModelRepository
from app.schemas.hair.color import ColorCreate, ColorUpdate, ColorInDB, SpecificColorInDB, SpecificColorCreate, SpecificColorUpdate
from app.schemas.hair.gender import GenderCreate, GenderUpdate, GenderInDB
from app.schemas.hair.hair_design import HairDesignCreate, HairDesignInDB, HairDesignUpdate
from app.schemas.hair.hair_design_color import HairDesignColorCreate, HairDesignColorInDB, HairDesignColorUpdate
from app.schemas.hair.hair_style import HairStyleCreate, HairStyleUpdate, HairStyleInDB
from app.schemas.hair.hair_style_length import HairStyleLengthCreate, HairStyleLengthInDB, HairStyleLengthUpdate
from app.schemas.hair.hair_variant_model import HairVariantModelCreate, HairVariantModelUpdate, HairVariantModelInDB
from app.schemas.hair.length import LengthCreate, LengthInDB, LengthUpdate
from app.schemas.hair.lora_model import LoRAModelCreate, LoRAModelInDB, LoRAModelUpdate
from app.services.base import BaseService


class GenderService(BaseService[Gender, GenderInDB, GenderCreate, GenderUpdate, GenderRepository]):
    def __init__(self, repo: GenderRepository):
        super().__init__(repo, GenderInDB)

class LengthService(BaseService[Length, LengthInDB, LengthCreate, LengthUpdate, LengthRepository]):
    def __init__(self, repo: LengthRepository):
        super().__init__(repo, LengthInDB)

class ColorService(BaseService[Color, ColorInDB, ColorCreate, ColorUpdate, ColorRepository]):
    def __init__(self, repo: ColorRepository):
        super().__init__(repo, ColorInDB)

class LoRAModelService(BaseService[LoRAModel, LoRAModelInDB, LoRAModelCreate, LoRAModelUpdate, LoRAModelRepository]):
    def __init__(self, repo: LoRAModelRepository):
        super().__init__(repo, LoRAModelInDB)

class SpecificColorService(BaseService[SpecificColor, SpecificColorInDB, SpecificColorCreate, SpecificColorUpdate, SpecificColorRepository]):
    def __init__(self, repo: SpecificColorRepository):
        super().__init__(repo, SpecificColorInDB)

class HairStyleService(BaseService[HairStyle, HairStyleInDB, HairStyleCreate, HairStyleUpdate, HairStyleRepository]):
    def __init__(self, repo: HairStyleRepository):
        super().__init__(repo, HairStyleInDB)

    def get_all_by_gender(self, gender_id: int) -> List[HairStyleInDB]:
        db_hair_style_list: List[HairStyle] = self.repo.get_all_by_gender(gender_id)
        return [HairStyleInDB.model_validate(db_hair_style) for db_hair_style in db_hair_style_list]

class HairStyleLengthService(BaseService[HairStyleLength, HairStyleLengthInDB, HairStyleLengthCreate, HairStyleLengthUpdate, HairStyleLengthRepository]):
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

class HairDesignService(BaseService[HairDesign, HairDesignInDB, HairDesignCreate, HairDesignUpdate, HairDesignRepository]):
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

class HairDesignColorService(BaseService[HairDesignColor, HairDesignColorInDB, HairDesignColorCreate, HairDesignColorUpdate, HairDesignColorRepository]):
    def __init__(self, repo: HairDesignColorRepository):
        super().__init__(repo,HairDesignColorInDB)

    def get_all_by_hair_design(self, hair_design_id: int) -> List[HairDesignColorInDB]:
        return [
            HairDesignColorInDB.model_validate(db_hair_design_color)
            for db_hair_design_color in self.repo.get_all_by_hair_design(hair_design_id)
        ]

class HairVariantModelService(BaseService[HairVariantModel,HairVariantModelInDB, HairVariantModelCreate, HairVariantModelUpdate, HairVariantModelRepository]):
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


