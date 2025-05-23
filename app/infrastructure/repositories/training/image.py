from sqlalchemy.orm import Session
from typing import List
from fastapi import Depends
from sqlalchemy import select
from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository

from app.domain.training.models.image import UploadedImageForTraining
from app.domain.training.schemas.image.uploaded_images_for_training import UploadedImagesForTrainingCreate, UploadedImagesForTrainingUpdate, UploadedImagesForTrainingInDB

class UploadedImageForTrainingRepository(CRUDRepository[UploadedImageForTraining, UploadedImagesForTrainingCreate, UploadedImagesForTrainingUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UploadedImageForTraining, db=db)
    
    def get_all_by_training_request(self, training_request_id: int) -> List[UploadedImageForTraining]:
        stmt = (
            select(UploadedImageForTraining)
            .where(UploadedImageForTraining.training_request_id == training_request_id)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())


def get_uploaded_image_for_training_repository(db: Session = Depends(get_db)) -> UploadedImageForTrainingRepository:
    return UploadedImageForTrainingRepository(db=db)
