from typing import List
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
from app.services.base import CRUDService, RelationValidatedCRUDService


class GenderService(CRUDService[Gender, GenderInDB, GenderCreate, GenderUpdate, GenderRepository]):
    def __init__(self, repo: GenderRepository):
        super().__init__(repo, GenderInDB)

class LengthService(CRUDService[Length, LengthInDB, LengthCreate, LengthUpdate, LengthRepository]):
    def __init__(self, repo: LengthRepository):
        super().__init__(repo, LengthInDB)

class ColorService(CRUDService[Color, ColorInDB, ColorCreate, ColorUpdate, ColorRepository]):
    def __init__(self, repo: ColorRepository):
        super().__init__(repo, ColorInDB)


class LoRAModelService(CRUDService[LoRAModel, LoRAModelInDB, LoRAModelCreate, LoRAModelUpdate, LoRAModelRepository]):
    def __init__(self, repo: LoRAModelRepository):
        super().__init__(repo, LoRAModelInDB)


class SpecificColorService(RelationValidatedCRUDService[SpecificColor, SpecificColorInDB, SpecificColorCreate, SpecificColorUpdate, SpecificColorRepository]):
    def __init__(
            self,
            repo: SpecificColorRepository,
            color_repo: ColorRepository
    ):
        super().__init__(
            repo=repo,
            model_in_db=SpecificColorInDB,
            relation_validators={
                "color_id": lambda id: color_repo.exists(id)
            }
        )


class HairStyleService(RelationValidatedCRUDService[HairStyle, HairStyleInDB, HairStyleCreate, HairStyleUpdate, HairStyleRepository]):
    def __init__(
            self,
            repo: HairStyleRepository,
            gender_repo: GenderRepository
    ):
        super().__init__(
            repo=repo,
            model_in_db=HairStyleInDB,
            relation_validators={
                "gender_id": lambda id: gender_repo.exists(id)
            }
        )
        # self.gender_repo = gender_repo

    def get_all_by_gender(self, gender_id: int) -> List[HairStyleInDB]:
        db_hair_style_list: List[HairStyle] = self.repo.get_all_by_gender(gender_id)
        return [HairStyleInDB.model_validate(db_hair_style) for db_hair_style in db_hair_style_list]


class HairStyleLengthService(RelationValidatedCRUDService[HairStyleLength, HairStyleLengthInDB, HairStyleLengthCreate, HairStyleLengthUpdate, HairStyleLengthRepository]):
    def __init__(
            self,
            repo: HairStyleLengthRepository,
            hair_style_repo: HairStyleRepository,
            length_repo: LengthRepository
    ):
        super().__init__(
            repo=repo,
            model_in_db=HairStyleLengthInDB,
            relation_validators={
                "hair_style_id": lambda id: hair_style_repo.exists(id),
                "length_id": lambda id: length_repo.exists(id)
            }
        )
        # self.hair_style_repo = hair_style_repo
        # self.length_repo = length_repo

    def get_all_by_hair_style(self, hair_style_id: int) -> List[HairStyleLengthInDB]:
        return [
            HairStyleLengthInDB.model_validate(db_hair_style_length)
            for db_hair_style_length in self.repo.get_all_by_hair_style(hair_style_id)
        ]

    def get_all_by_length(self, length_id: int) -> List[HairStyleLengthInDB]:
        return [
            HairStyleLengthInDB.model_validate(db_hair_style_length)
            for db_hair_style_length in self.repo.get_all_by_length(length_id)
        ]

class HairDesignService(RelationValidatedCRUDService[HairDesign, HairDesignInDB, HairDesignCreate, HairDesignUpdate, HairDesignRepository]):
    def __init__(
            self,
            repo: HairDesignRepository,
            hair_style_repo: HairStyleRepository,
            length_repo: LengthRepository
    ):
        super().__init__(
            repo=repo,
            model_in_db=HairDesignInDB,
            relation_validators={
                "hair_style_id": lambda id: hair_style_repo.exists(id),
                "length_id": lambda id: length_repo.exists(id)
            }
        )

    def get_all_by_hair_style(self, hair_style_id: int) -> List[HairDesignInDB]:
        return [
            HairDesignInDB.model_validate(db_hair_design)
            for db_hair_design in self.repo.get_all_by_hair_style(hair_style_id)
        ]

    def get_all_by_length(self, length_id: int) -> List[HairDesignInDB]:
        return [
            HairDesignInDB.model_validate(db_hair_style_length)
            for db_hair_style_length in self.repo.get_all_by_length(length_id)
        ]

class HairDesignColorService(RelationValidatedCRUDService[HairDesignColor, HairDesignColorInDB, HairDesignColorCreate, HairDesignColorUpdate, HairDesignColorRepository]):
    def __init__(
            self,
            repo: HairDesignColorRepository,
            hair_design_repo: HairDesignRepository,
            color_repo: ColorRepository
    ):
        super().__init__(
            repo=repo,
            model_in_db=HairDesignColorInDB,
            relation_validators={
                "hair_design_id": lambda id: hair_design_repo.exists(id),
                "color_id": lambda id: color_repo.exists(id)
            }
        )

    def get_all_by_hair_design(self, hair_design_id: int) -> List[HairDesignColorInDB]:
        return [
            HairDesignColorInDB.model_validate(db_hair_design_color)
            for db_hair_design_color in self.repo.get_all_by_hair_design(hair_design_id)
        ]

class HairVariantModelService(RelationValidatedCRUDService[HairVariantModel,HairVariantModelInDB, HairVariantModelCreate, HairVariantModelUpdate, HairVariantModelRepository]):
    def __init__(
            self,
            repo: HairVariantModelRepository,
            hair_design_color_repo: HairDesignColorRepository,
            lora_model_repo: LoRAModelRepository
    ):
        super().__init__(
            repo=repo,
            model_in_db=HairVariantModelInDB,
            relation_validators={
                "hair_design_color_id": lambda id: hair_design_color_repo.exists(id),
                "lora_model_id": lambda id: lora_model_repo.exists(id)
            }
        )

    def get_all_by_hair_design_color(self, hair_design_color_id: int) -> List[HairVariantModelInDB]:
        return [
            HairVariantModelInDB.model_validate(db_hair_variant_model)
            for db_hair_variant_model in self.repo.get_all_by_hair_design_color(hair_design_color_id)
        ]


