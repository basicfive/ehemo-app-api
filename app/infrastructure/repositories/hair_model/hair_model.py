from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import update, select, func, and_
from typing import List, Tuple
from collections import defaultdict
from fastapi import Depends

from app.core.db.base import get_db
from app.domain.hair_model.models.scene import Background, PostureAndClothing, ImageResolution
from app.domain.hair_model.schemas.scene.background import BackgroundCreate, BackgroundUpdate
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionCreate, ImageResolutionUpdate
from app.domain.hair_model.schemas.scene.posture_and_clothing import PostureAndClothingUpdate, PostureAndClothingCreate
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.hair_model.schemas.hair.color import ColorCreate, ColorUpdate, SpecificColorCreate, SpecificColorUpdate
from app.domain.hair_model.schemas.hair.gender import *
from app.domain.hair_model.models.hair import Gender, HairStyle, Length, Color, SpecificColor, LoRAModel, HairStyleLength, HairDesign, \
    HairDesignColor, HairVariantModel
from app.domain.hair_model.schemas.hair.hair_design import HairDesignCreate, HairDesignUpdate
from app.domain.hair_model.schemas.hair.hair_design_color import HairDesignColorCreate, HairDesignColorUpdate
from app.domain.hair_model.schemas.hair.hair_style import HairStyleCreate, HairStyleUpdate
from app.domain.hair_model.schemas.hair.hair_style_length import HairStyleLengthCreate, HairStyleLengthUpdate
from app.domain.hair_model.schemas.hair.hair_variant_model import HairVariantModelCreate, HairVariantModelUpdate
from app.domain.hair_model.schemas.hair.length import LengthCreate, LengthUpdate
from app.domain.hair_model.schemas.hair.lora_model import LoRAModelCreate, LoRAModelUpdate


class GenderRepository(CRUDRepository[Gender, GenderCreate, GenderUpdate]):
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

def get_gender_repository(db: Session = Depends(get_db)) -> GenderRepository:
    return GenderRepository(db=db)


class HairStyleRepository(CRUDRepository[HairStyle, HairStyleCreate, HairStyleUpdate]):
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

def get_hair_style_repository(db: Session = Depends(get_db)) -> HairStyleRepository:
    return HairStyleRepository(db=db)


class LengthRepository(CRUDRepository[Length, LengthCreate, LengthUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Length, db=db)
        self.db = db

def get_length_repository(db: Session = Depends(get_db)) -> LengthRepository:
    return LengthRepository(db=db)


class ColorRepository(CRUDRepository[Color, ColorCreate, ColorUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Color, db=db)
        self.db = db

def get_color_repository(db: Session = Depends(get_db)) -> ColorRepository:
    return ColorRepository(db=db)


class SpecificColorRepository(CRUDRepository[SpecificColor, SpecificColorCreate, SpecificColorUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=SpecificColor, db=db)
        self.db = db

    def get_all_by_color(self, color_id: int) -> List[SpecificColor]:
        stmt = select(SpecificColor).where(SpecificColor.color_id == color_id)
        return list(self.db.scalars(stmt).all())

    def get_all_by_color_limit(self, color_id: int, limit: int = 10) -> List[SpecificColor]:
        stmt = select(SpecificColor).where(SpecificColor.color_id == color_id).limit(limit)
        return list(self.db.scalars(stmt).all())

def get_specific_color_repository(db: Session = Depends(get_db)) -> SpecificColorRepository:
    return SpecificColorRepository(db=db)


class LoRAModelRepository(CRUDRepository[LoRAModel, LoRAModelCreate, LoRAModelUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=LoRAModel, db=db)
        self.db = db

def get_lora_model_repository(db: Session = Depends(get_db)) -> LoRAModelRepository:
    return LoRAModelRepository(db=db)


class HairStyleLengthRepository(CRUDRepository[HairStyleLength, HairStyleLengthCreate, HairStyleLengthUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairStyleLength, db=db)
        self.db = db

    def get_all_by_length(self, length_id: int) -> List[HairStyleLength]:
        return self.db.query(HairStyleLength).filter(HairStyleLength.length_id == length_id).all()

    def get_all_by_hair_style(self, hair_style_id: int) -> List[HairStyleLength]:
        return self.db.query(HairStyleLength).filter(HairStyleLength.hair_style_id == hair_style_id).all()

    def get_all_by_hair_style_with_length(self, hair_style_id: int) -> List[HairStyleLength]:
        stmt = (
            select(HairStyleLength)
            .options(joinedload(HairStyleLength.length))
            .where(HairStyleLength.hair_style_id == hair_style_id)
        )
        return list(self.db.scalars(stmt).all())


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


def get_hair_style_length_repository(db: Session = Depends(get_db)) -> HairStyleLengthRepository:
    return HairStyleLengthRepository(db=db)


class HairDesignRepository(CRUDRepository[HairDesign, HairDesignCreate, HairDesignUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairDesign, db=db)
        self.db = db

    def get_all_by_hair_style(self, hair_style_id: int) -> List[HairDesign]:
        stmt = select(HairDesign).where(HairDesign.hair_style_id == hair_style_id)
        return list(self.db.scalars(stmt).all())

    def get_by_hair_style_and_length(self, hair_style_id: int, length_id: int):
        stmt = select(HairDesign).where(
            and_(
                HairDesign.hair_style_id == hair_style_id,
                HairDesign.length_id == length_id
            )
        )

        try:
            return self.db.execute(stmt).scalar_one()
        except NoResultFound:
            raise ValueError(f"HairDesign with hairstyle id: {hair_style_id}, length_id: {length_id} does not exist in the database")


def get_hair_design_repository(db: Session = Depends(get_db)) -> HairDesignRepository:
    return HairDesignRepository(db=db)


class HairDesignColorRepository(CRUDRepository[HairDesignColor, HairDesignColorCreate, HairDesignColorUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairDesignColor, db=db)
        self.db = db

    def get_all_by_hair_design(self, hair_design_id: int) -> List[HairDesignColor]:
        return self.db.query(HairDesignColor).filter(HairDesignColor.hair_design_id == hair_design_id).all()

    def get_all_by_hair_design_with_color(self, hair_design_id: int) -> List[HairDesignColor]:
        stmt = (
            select(HairDesignColor)
            .options(joinedload(HairDesignColor.color))
            .where(HairDesignColor.hair_design_id == hair_design_id)
        )
        return list(self.db.scalars(stmt).all())

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

def get_hair_design_color_repository(db: Session = Depends(get_db)) -> HairDesignColorRepository:
    return HairDesignColorRepository(db=db)

class HairVariantModelRepository(CRUDRepository[HairVariantModel, HairVariantModelCreate, HairVariantModelUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairVariantModel, db=db)
        self.db = db

    def get_by_hair_style_length_color(self, hair_style_id: int, length_id: Optional[int], color_id: int) -> HairVariantModel:
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
        stmt = select(HairVariantModel).where(HairVariantModel.is_published == True)
        return list(self.db.scalars(stmt).all())

def get_hair_variant_model_repository(db: Session = Depends(get_db)) -> HairVariantModelRepository:
    return HairVariantModelRepository(db=db)


class BackgroundRepository(CRUDRepository[Background, BackgroundCreate, BackgroundUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Background, db=db)
        self.db = db

def get_background_repository(db: Session = Depends(get_db)) -> BackgroundRepository:
    return BackgroundRepository(db=db)


class PostureAndClothingRepository(CRUDRepository[PostureAndClothing, PostureAndClothingCreate, PostureAndClothingUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=PostureAndClothing, db=db)
        self.db = db

    def get_random_records_in_gender(self, gender_id: int, limit: int = 10) -> List[PostureAndClothing]:
        stmt = select(PostureAndClothing).where(PostureAndClothing.gender_id == gender_id).order_by(func.random()).limit(limit)
        return list(self.db.scalars(stmt).all())

def get_posture_and_clothing_repository(db: Session = Depends(get_db)) -> PostureAndClothingRepository:
    return PostureAndClothingRepository(db=db)


class ImageResolutionRepository(CRUDRepository[ImageResolution, ImageResolutionCreate, ImageResolutionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageResolution, db=db)
        self.db = db

def get_image_resolution_repository(db: Session = Depends(get_db)) -> ImageResolutionRepository:
    return ImageResolutionRepository(db=db)
