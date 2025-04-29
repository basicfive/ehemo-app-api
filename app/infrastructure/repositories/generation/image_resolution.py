from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db.base import get_db
from app.domain.generation.models.image_resolution import ImageResolution, ImageRatio
from app.domain.generation.schemas.image_resolution.image_resolution import ImageResolutionCreate, ImageResolutionUpdate
from app.domain.generation.schemas.image_resolution.image_ratio import ImageRatioCreate, ImageRatioUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository

class ImageRatioRepository(CRUDRepository[ImageRatio, ImageRatioCreate, ImageRatioUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageRatio, db=db)

def get_image_ratio_repository(db: Session = Depends(get_db)) -> ImageRatioRepository:
    return ImageRatioRepository(db=db)

class ImageResolutionRepository(CRUDRepository[ImageResolution, ImageResolutionCreate, ImageResolutionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageResolution, db=db)

    def get_by_ratio_and_is_high_res(self, ratio_id: int, is_high_res: bool) -> ImageResolution:
        stmt = (
            select(ImageResolution)
            .where(
                ImageResolution.image_ratio_id == ratio_id,
                ImageResolution.is_high_resolution == is_high_res
            )
        )
        return self.db.execute(stmt).scalars().first()

def get_image_resolution_repository(db: Session = Depends(get_db)) -> ImageResolutionRepository:
    return ImageResolutionRepository(db=db)
