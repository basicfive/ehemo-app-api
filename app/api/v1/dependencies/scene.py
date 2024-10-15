from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.scene import BackgroundRepository, PostureAndClothingRepository, ImageResolutionRepository
from app.services.scene import BackgroundService, PostureAndClothingService, ImageResolutionService


def get_background_repository(db: Session = Depends(get_db)) -> BackgroundRepository:
    return BackgroundRepository(db=db)

def get_posture_and_clothing_repository(db: Session = Depends(get_db)) -> PostureAndClothingRepository:
    return PostureAndClothingRepository(db=db)

def get_image_resolution_repository(db: Session = Depends(get_db)) -> ImageResolutionRepository:
    return ImageResolutionRepository(db=db)

def get_background_service(repo: BackgroundRepository = Depends(get_background_repository)) -> BackgroundService:
    return BackgroundService(repo=repo)

def get_posture_and_clothing_service(repo: PostureAndClothingRepository = Depends(get_posture_and_clothing_repository)) -> PostureAndClothingService:
    return PostureAndClothingService(repo=repo)

def get_image_resolution_service(repo: ImageResolutionRepository = Depends(get_image_resolution_repository)) -> ImageResolutionService:
    return ImageResolutionService(repo=repo)
