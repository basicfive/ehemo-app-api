from app.models.scene import Background, PostureAndClothing, ImageResolution
from app.repositories.scene import BackgroundRepository, PostureAndClothingRepository, ImageResolutionRepository
from app.schemas.scene.background import BackgroundInDB, BackgroundCreate
from app.schemas.scene.image_resolution import ImageResolutionInDB, ImageResolutionCreate, ImageResolutionUpdate
from app.schemas.scene.posture_and_clothing import PostureAndClothingInDB, PostureAndClothingCreate, PostureAndClothingUpdate
from app.services.base import CRUDService

class BackgroundService(CRUDService[Background, BackgroundInDB, BackgroundCreate, BackgroundCreate, BackgroundRepository]):
    def __init__(self, repo: BackgroundRepository):
        super().__init__(repo=repo, model_in_db=BackgroundInDB)


class PostureAndClothingService(
    CRUDService[PostureAndClothing, PostureAndClothingInDB, PostureAndClothingCreate, PostureAndClothingUpdate, PostureAndClothingRepository]
):
    def __init__(self, repo: PostureAndClothingRepository):
        super().__init__(repo=repo, model_in_db=PostureAndClothingInDB)


class ImageResolutionService(
    CRUDService[ImageResolution, ImageResolutionInDB, ImageResolutionCreate, ImageResolutionUpdate, ImageResolutionRepository]
):
    def __init__(self, repo: ImageResolutionRepository):
        super().__init__(repo=repo, model_in_db=ImageResolutionInDB)