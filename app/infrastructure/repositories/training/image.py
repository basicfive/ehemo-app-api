from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository

from app.domain.training.models.image import UploadedImagesForTraining, TrainingRequestUploadedImages
from app.domain.training.schemas.image.uploaded_images_for_training import UploadedImagesForTrainingCreate, UploadedImagesForTrainingUpdate, UploadedImagesForTrainingInDB
from app.domain.training.schemas.image.training_request_uploaded_images import TrainingRequestUploadedImagesCreate, TrainingRequestUploadedImagesUpdate, TrainingRequestUploadedImagesInDB



class UploadedImagesForTrainingRepository(CRUDRepository[UploadedImagesForTraining, UploadedImagesForTrainingCreate, UploadedImagesForTrainingUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UploadedImagesForTraining, db=db)


def get_uploaded_images_for_training_repository(db: Session = Depends(get_db)) -> UploadedImagesForTrainingRepository:
    return UploadedImagesForTrainingRepository(db=db)


class TrainingRequestUploadedImagesRepository(CRUDRepository[TrainingRequestUploadedImages, TrainingRequestUploadedImagesCreate, TrainingRequestUploadedImagesUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=TrainingRequestUploadedImages, db=db)

def get_training_request_uploaded_images_repository(db: Session = Depends(get_db)) -> TrainingRequestUploadedImagesRepository:
    return TrainingRequestUploadedImagesRepository(db=db)



