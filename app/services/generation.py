from app.models.generation import GenerationRequest
from app.repositories.generation import GenerationRequestRepository, ImageGenerationJobRepository
from app.schemas.generation.generation_request import GenerationRequestCreate, GenerationRequestUpdate, GenerationRequestInDB
from app.schemas.generation.image_generation_job import ImageGenerationJobInDB, ImageGenerationJobCreate, \
    ImageGenerationJobUpdate
from app.services.base import BaseService

class GenerationRequestService(BaseService[GenerationRequest, GenerationRequestInDB, GenerationRequestCreate, GenerationRequestUpdate, GenerationRequestRepository]):
    def __init__(self, repo=GenerationRequestRepository):
        super().__init__(repo=repo, model_in_db=GenerationRequestInDB)

class ImageGenerationJobService(BaseService[ImageGenerationJobInDB, ImageGenerationJobInDB, ImageGenerationJobCreate, ImageGenerationJobUpdate, ImageGenerationJobRepository]):
    def __init__(self, repo=ImageGenerationJobRepository):
        super().__init__(repo=repo, model_in_db=ImageGenerationJobInDB)