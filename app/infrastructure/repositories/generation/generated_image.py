from fastapi import Depends
from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from sqlalchemy.orm.query import Query

from app.domain.generation.enums.generated_image_status import GeneratedImageStatus
from app.core.db.base import get_db
from app.domain.generation.models.generated_image import GeneratedImage
from app.domain.generation.models.generation import GenerationJob, GenerationRequest
from app.domain.generation.models.image_resolution import ImageResolution
from app.domain.generation.schemas.generated_image.generated_image import GeneratedImageCreate, GeneratedImageUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository

class GeneratedImageRepository(CRUDRepository[GeneratedImage, GeneratedImageCreate, GeneratedImageUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImage, db=db)
    
    def get_all_in_generation_jobs_with_job(self, generation_job_ids: List[int]) -> List[GeneratedImage]:
        stmt = (
            select(GeneratedImage)
            .where(GeneratedImage.generation_job_id.in_(generation_job_ids))
            .options(joinedload(GeneratedImage.generation_job))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_upscaled_user_generated_images_with_job(self, user_id: int) -> List[GeneratedImage]:
        stmt = select(GeneratedImage).filter(
            GeneratedImage.user_id == user_id,
            GeneratedImage.status == GeneratedImageStatus.UPSCALED,
        ).options(joinedload(GeneratedImage.generation_job))
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_any_by_generation_job_id(self, generation_job_id: int) -> GeneratedImage:
        stmt = select(GeneratedImage).filter(GeneratedImage.generation_job_id == generation_job_id)
        result = self.db.execute(stmt)
        return result.scalars().first()

    def get_all_by_generation_job_id(self, generation_job_id: int) -> List[GeneratedImage]:
        stmt = select(GeneratedImage).filter(GeneratedImage.generation_job_id == generation_job_id)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_all_by_generation_request_id(self, generation_request_id: int) -> List[GeneratedImage]:
        stmt = (
            select(GeneratedImage)
            .join(GenerationJob, GeneratedImage.generation_job_id == GenerationJob.id)
            .where(GenerationJob.generation_request_id == generation_request_id)
            .options(joinedload(GeneratedImage.generation_job))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())


def get_generated_image_repository(db: Session = Depends(get_db)) -> GeneratedImageRepository:
    return GeneratedImageRepository(db=db)
