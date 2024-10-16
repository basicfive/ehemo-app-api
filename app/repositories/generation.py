from sqlalchemy.orm import Session

from app.models.generation import GenerationRequest
from app.repositories.base import BaseRepository
from app.schemas.generation.generation_request import GenerationRequestCreate, GenerationRequestUpdate
from app.schemas.generation.image_generation_job import ImageGenerationJobInDB, ImageGenerationJobCreate, \
    ImageGenerationJobUpdate


class GenerationRequestRepository(BaseRepository[GenerationRequest, GenerationRequestCreate, GenerationRequestUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GenerationRequest, db=db)

class ImageGenerationJobRepository(BaseRepository[ImageGenerationJobInDB, ImageGenerationJobCreate, ImageGenerationJobUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageGenerationJobInDB, db=db)
    