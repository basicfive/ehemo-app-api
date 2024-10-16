from sqlalchemy.orm import Session

from app.models.image import GeneratedImage, GeneratedImageGroup
from app.repositories.base import BaseRepository
from app.schemas.image.generated_image import GeneratedImageCreate, GeneratedImageUpdate

class GeneratedImageRepository(BaseRepository[GeneratedImage, GeneratedImageCreate, GeneratedImageUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImage, db=db)
        
class GeneratedImageGroupRepository(BaseRepository[GeneratedImageGroup, GeneratedImageCreate, GeneratedImageUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImageGroup, db=db)
