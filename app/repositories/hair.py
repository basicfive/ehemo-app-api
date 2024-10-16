from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy import update, select
from typing import List, Tuple, Type
from collections import defaultdict

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

    def get_all_by_hair_style_and_length_set(self, pairs: List[Tuple[int, int]]) -> List[HairStyleLength]:
        if not pairs:
            return []

        unique_pairs = set(pairs)

        # hair_style_id를 기준으로 그룹화
        hair_style_groups = defaultdict(set)
        for hair_style_id, length_id in unique_pairs:
            hair_style_groups[hair_style_id].add(length_id)

        stmt = select(HairStyleLength).where(
            HairStyleLength.hair_style_id.in_(hair_style_groups.keys())
        )

        result = self.db.execute(stmt)
        all_matches = result.scalars().all()

        filtered_results = [
            match for match in all_matches
            if match.length_id in hair_style_groups[match.hair_style_id]
        ]

        return filtered_results

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

    def get_all_by_hair_style(self, hair_style_id: int):
        self.db.query(HairDesign).filter(HairDesign.hair_style_id.is_(hair_style_id)).all()

    def get_all_by_hair_style_and_length(self, hair_style_id: int, length_id: int):
        stmt = select(HairDesign).where(
            (HairDesign.hair_style_id.is_(hair_style_id)) &
            (HairDesign.length_id.is_(length_id))
        )

        try:
            result = self.db.execute(stmt)
            return result.scalars().all()
        except NoResultFound:
            raise ValueError(f"HairDesign with hairstyle id: {hair_style_id}, length_id: {length_id} does not exist in the database")

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

    def get_by_hair_style_length_color(self, hair_style_id: int, length_id: int, color_id: int) -> HairVariantModel:
        stmt = select(HairVariantModel).filter_by(
            hair_style_id=hair_style_id,
            length_id=length_id,
            color_id=color_id
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if not result:
            raise ValueError(
                f"There is no corresponding HairVariantModel with hs_id: {hair_style_id}, length_id: {length_id}, color_id: {color_id}")
        return result

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