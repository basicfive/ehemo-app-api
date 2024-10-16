from typing import List

from app.models.scene import Background, PostureAndClothing, ImageResolution
from app.repositories.scene import BackgroundRepository, PostureAndClothingRepository, ImageResolutionRepository
from app.schemas.scene.background import BackgroundInDB, BackgroundCreate
from app.schemas.scene.image_resolution import ImageResolutionInDB, ImageResolutionCreate, ImageResolutionUpdate
from app.schemas.scene.posture_and_clothing import PostureAndClothingInDB, PostureAndClothingCreate, PostureAndClothingUpdate
from app.services.base import BaseService

class BackgroundService(BaseService[Background, BackgroundInDB, BackgroundCreate, BackgroundCreate, BackgroundRepository]):
    def __init__(self, repo: BackgroundRepository):
        super().__init__(repo=repo, model_in_db=BackgroundInDB)


class PostureAndClothingService(
    BaseService[PostureAndClothing, PostureAndClothingInDB, PostureAndClothingCreate, PostureAndClothingUpdate, PostureAndClothingRepository]
):
    def __init__(self, repo: PostureAndClothingRepository):
        super().__init__(repo=repo, model_in_db=PostureAndClothingInDB)

    def get_random_posture_and_clothing(self, limit=10):
        posture_and_clothing_list: List[PostureAndClothing] = self.repo.get_random_records(limit=limit)
        return [PostureAndClothingInDB.model_validate(posture_and_clothing) for posture_and_clothing in posture_and_clothing_list]

class ImageResolutionService(
    BaseService[ImageResolution, ImageResolutionInDB, ImageResolutionCreate, ImageResolutionUpdate, ImageResolutionRepository]
):
    def __init__(self, repo: ImageResolutionRepository):
        super().__init__(repo=repo, model_in_db=ImageResolutionInDB)