from typing import List

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db.base import get_db
from app.domain import ImageRatio, BackgroundForMatting
from app.domain.hair_model.models.scene import Background, PostureAndClothing, ImageResolution
from app.domain.hair_model.schemas.scene.background import BackgroundCreate, BackgroundUpdate
from app.domain.hair_model.schemas.scene.background_for_matting import BackgroundForMattingCreate, \
    BackgroundForMattingUpdate
from app.domain.hair_model.schemas.scene.image_ratio import ImageRatioCreate, ImageRatioUpdate
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionCreate, ImageResolutionUpdate
from app.domain.hair_model.schemas.scene.posture_and_clothing import PostureAndClothingUpdate, PostureAndClothingCreate
from app.infrastructure.repositories.crud_repository import CRUDRepository


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

class ImageRatioRepository(CRUDRepository[ImageRatio, ImageRatioCreate, ImageRatioUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageRatio, db=db)
        self.db = db

def get_image_ratio_repository(db: Session = Depends(get_db)) -> ImageRatioRepository:
    return ImageRatioRepository(db=db)

class ImageResolutionRepository(CRUDRepository[ImageResolution, ImageResolutionCreate, ImageResolutionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageResolution, db=db)
        self.db = db

    def get_by_ratio(self, image_ratio_id: int) -> List[ImageResolution]:
        stmt = select(ImageResolution).where(ImageResolution.image_ratio_id == image_ratio_id)
        return list(self.db.scalars(stmt).all())

def get_image_resolution_repository(db: Session = Depends(get_db)) -> ImageResolutionRepository:
    return ImageResolutionRepository(db=db)

class BackgroundForMattingRepository(CRUDRepository[BackgroundForMatting, BackgroundForMattingCreate, BackgroundForMattingUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=BackgroundForMatting, db=db)
        self.db = db

    def get_by_resolution(self, image_resolution_id: int) -> BackgroundForMatting:
        stmt = select(BackgroundForMatting).where(BackgroundForMatting.image_resolution_id == image_resolution_id)
        return self.db.execute(stmt).scalar_one()

def get_background_for_matting_repo(db: Session = Depends(get_db)) -> BackgroundForMattingRepository:
    return BackgroundForMattingRepository(db=db)


