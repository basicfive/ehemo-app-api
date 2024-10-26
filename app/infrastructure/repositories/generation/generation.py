from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.base import get_db
from app.domain.generation.models.generation import GenerationRequest, ImageGenerationJob
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupCreate, GeneratedImageGroupUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.generation.schemas.generation_request import GenerationRequestCreate, GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobCreate, ImageGenerationJobUpdate
from app.domain.generation.models.image import GeneratedImage, GeneratedImageGroup
from app.domain.generation.schemas.generated_image import GeneratedImageCreate, GeneratedImageUpdate


class GenerationRequestRepository(CRUDRepository[GenerationRequest, GenerationRequestCreate, GenerationRequestUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GenerationRequest, db=db)

def get_generation_request_repository(db: Session = Depends(get_db)) -> GenerationRequestRepository:
    return GenerationRequestRepository(db=db)

class ImageGenerationJobRepository(CRUDRepository[ImageGenerationJob, ImageGenerationJobCreate, ImageGenerationJobUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageGenerationJob, db=db)

    def get_all_by_generation_request(self, generation_request_id: int) -> List[ImageGenerationJob]:
        stmt = select(ImageGenerationJob).where(ImageGenerationJob.generation_request_id == generation_request_id)
        return list(self.db.scalars(stmt).all())

def get_image_generation_job_repository(db: Session = Depends(get_db)) -> ImageGenerationJobRepository:
    return ImageGenerationJobRepository(db=db)

class GeneratedImageRepository(CRUDRepository[GeneratedImage, GeneratedImageCreate, GeneratedImageUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImage, db=db)

    def get_all_by_generate_image_group(self, generated_image_group_id: int) -> List[GeneratedImage]:
        stmt = select(GeneratedImage).where(GeneratedImage.generated_image_group_id == generated_image_group_id)
        return list(self.db.scalars(stmt).all())

def get_generated_image_repository(db: Session = Depends(get_db)) -> GeneratedImageRepository:
    return GeneratedImageRepository(db=db)

class GeneratedImageGroupRepository(CRUDRepository[GeneratedImageGroup, GeneratedImageGroupCreate, GeneratedImageGroupUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImageGroup, db=db)

    def get_all_by_user(self, user_id: int) -> List[GeneratedImageGroup]:
        stmt = select(GeneratedImageGroup).where(GeneratedImageGroup.user_id == user_id)
        return list(self.db.scalars(stmt).all())

    def get_by_generation_request(self, generation_request_id: int) -> GeneratedImageGroup:
        stmt = select(GeneratedImageGroup).where(GeneratedImageGroup.generation_request_id == generation_request_id)
        result = self.db.execute(stmt)
        return result.scalar_one()

def get_generated_image_group_repository(db: Session = Depends(get_db)) -> GeneratedImageGroupRepository:
    return GeneratedImageGroupRepository(db=db)
