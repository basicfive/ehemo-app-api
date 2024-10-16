from app.models.image import GeneratedImage, GeneratedImageGroup
from app.repositories.image import GeneratedImageRepository, GeneratedImageGroupRepository
from app.schemas.image.generated_image import GeneratedImageInDB, GeneratedImageCreate, GeneratedImageUpdate
from app.schemas.image.generated_image_group import GeneratedImageGroupInDB, GeneratedImageGroupCreate, \
    GeneratedImageGroupUpdate
from app.services.base import BaseService


class GeneratedImageService(BaseService[GeneratedImage, GeneratedImageInDB, GeneratedImageCreate, GeneratedImageUpdate, GeneratedImageRepository]):
    def __init__(self, repo: GeneratedImageRepository):
        super().__init__(repo=repo, model_in_db=GeneratedImageInDB)

class GeneratedImageGroupService(BaseService[GeneratedImageGroup, GeneratedImageGroupInDB, GeneratedImageGroupCreate, GeneratedImageGroupUpdate, GeneratedImageGroupRepository]):
    def __init__(self, repo: GeneratedImageGroupRepository):
        super().__init__(repo=repo, model_in_db=GeneratedImageGroupInDB)
