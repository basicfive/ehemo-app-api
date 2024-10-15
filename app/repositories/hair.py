from sqlalchemy.orm import Session
from sqlalchemy import update, or_, and_, select
from typing import List, Tuple

from app.repositories.base import BaseRepository
from app.schemas.hair.color import ColorCreate, ColorUpdate, SpecificColorCreate, SpecificColorUpdate
from app.schemas.hair.gender import *
from app.models.hair import Gender, HairStyle, Length, Color, SpecificColor, LoRAModel, HairStyleLength, HairDesign, \
    HairDesignColor, HairVariantModel
from app.schemas.hair.hair_design import HairDesignCreate, HairDesignUpdate
from app.schemas.hair.hair_design_color import HairDesignColorCreate, HairDesignColorUpdate
from app.schemas.hair.hair_style import HairStyleCreate, HairStyleUpdate
from app.schemas.hair.hair_style_length import HairStyleLengthCreate, HairStyleLengthUpdate
from app.schemas.hair.hair_variant_model import HairVariantModelCreate, HairVariantModelUpdate
from app.schemas.hair.length import LengthCreate, LengthUpdate
from app.schemas.hair.lora_model import LoRAModelCreate, LoRAModelUpdate


class GenderRepository(BaseRepository[Gender, GenderCreate, GenderUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Gender, db=db)
        self.db = db

    def update_is_published(self, ids: List[int], is_published: bool):
        stmt = (
            update(Gender)
            .where(Gender.id.in_(ids))
            .values(is_published=is_published)
        )
        self.db.execute(stmt)
        self.db.commit()


class HairStyleRepository(BaseRepository[HairStyle, HairStyleCreate, HairStyleUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairStyle, db=db)
        self.db = db

    def get_all_by_gender(self, gender_id: int) -> List[HairStyle]:
        return self.db.query(HairStyle).filter(HairStyle.gender_id == gender_id).all()

    def update_is_published(self, ids: List[int], is_published: bool):
        stmt = (
            update(HairStyle)
            .where(HairStyle.id.in_(ids))
            .values(is_published=is_published)
        )
        self.db.execute(stmt)
        self.db.commit()


class LengthRepository(BaseRepository[Length, LengthCreate, LengthUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Length, db=db)
        self.db = db

class ColorRepository(BaseRepository[Color, ColorCreate, ColorUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Color, db=db)
        self.db = db

class SpecificColorRepository(BaseRepository[SpecificColor, SpecificColorCreate, SpecificColorUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=SpecificColor, db=db)
        self.db = db

    def get_all_by_color(self, color_id: int) -> List[Color]:
        return self.db.query(SpecificColor).filter(SpecificColor.color_id == color_id).all()

class LoRAModelRepository(BaseRepository[LoRAModel, LoRAModelCreate, LoRAModelUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=LoRAModel, db=db)
        self.db = db

class HairStyleLengthRepository(BaseRepository[HairStyleLength, HairStyleLengthCreate, HairStyleLengthUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairStyleLength, db=db)
        self.db = db

    def get_all_by_length(self, length_id: int):
        self.db.query(HairStyleLength).filter(HairStyleLength.length_id == length_id).all()

    def get_all_by_hair_style(self, hair_style_id: int):
        self.db.query(HairStyleLength).filter(HairStyleLength.hair_style_id == hair_style_id).all()

    # TODO: n*n 연산임.(얼마 안되는 n 이지만) 이를 피하기 위해 구조적으로 변경할 수 있는게 있을까?
    def get_all_by_hair_style_and_length(self, pairs: List[Tuple[int, int]]) -> List[HairStyleLength]:
        if not pairs:
            return []

        unique_pairs = set(pairs)

        conditions = [
            and_(
                HairStyleLength.hair_style_id == pair[0],
                HairStyleLength.length_id == pair[1]
            )
            for pair in unique_pairs
        ]

        stmt = select(HairStyleLength).where(or_(*conditions))

        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def update_is_published(self, ids: List[int], is_published: bool):
        stmt = (
            update(HairStyleLength)
            .where(HairStyleLength.id.in_(ids))
            .values(is_published=is_published)
        )
        self.db.execute(stmt)
        self.db.commit()

class HairDesignRepository(BaseRepository[HairDesign, HairDesignCreate, HairDesignUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairDesign, db=db)
        self.db = db

    def get_all_by_length(self, length_id: int):
        self.db.query(HairDesign).filter(HairDesign.length_id == length_id).all()

    def get_all_by_hair_style(self, hair_style_id: int):
        self.db.query(HairDesign).filter(HairDesign.hair_style_id == hair_style_id).all()




class HairDesignColorRepository(BaseRepository[HairDesignColor, HairDesignColorCreate, HairDesignColorUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairDesignColor, db=db)
        self.db = db

    def get_all_by_hair_design(self, hair_design_id: int) -> List[HairDesignColor]:
        return self.db.query(HairDesignColor).filter(HairDesignColor.hair_design_id == hair_design_id).all()

    def get_all_by_color(self, color_id: int) -> List[HairDesignColor]:
        return self.db.query(HairDesignColor).filter(HairDesignColor.color_id == color_id).all()

    def update_is_published(self, ids: List[int], is_published: bool):
        stmt = (
            update(HairDesignColor)
            .where(HairDesignColor.id.in_(ids))
            .values(is_published=is_published)
        )
        self.db.execute(stmt)
        self.db.commit()

class HairVariantModelRepository(BaseRepository[HairVariantModel, HairVariantModelCreate, HairVariantModelUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairVariantModel, db=db)
        self.db = db

    def get_all_by_hair_design_color(self, hair_design_color_id: int) -> List[HairVariantModel]:
        return self.db.query(HairVariantModel).filter(HairVariantModel.hair_design_color_id == hair_design_color_id).all()

    def get_all_by_lora_model(self, lora_model_id: int) -> List[HairVariantModel]:
        return self.db.query(HairVariantModel).filter(HairVariantModel.lora_model_id == lora_model_id).all()

    def get_all_unpublished(self) -> List[HairVariantModel]:
        return self.db.query(HairVariantModel).filter(HairVariantModel.is_published == False).all()

    def update_is_published(self, ids: List[int], is_published: bool):
        stmt = (
            update(HairVariantModel)
            .where(HairVariantModel.id.in_(ids))
            .values(is_published=is_published)
        )
        self.db.execute(stmt)
        self.db.commit()

    def get_all_published(self) -> List[HairVariantModel]:
        return self.db.query(HairVariantModel).filter(HairVariantModel.is_published == True).all()