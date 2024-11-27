from typing import List

from fastapi import Depends
from sqlalchemy import select, update, and_
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, UTC

from app.core.db.base import get_db
from app.core.enums.generation_status import GenerationStatusEnum
from app.domain.generation.models.generation import GenerationRequest, ImageGenerationJob
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupCreate, GeneratedImageGroupUpdate
from app.domain.hair_model.models.hair import HairVariantModel, HairStyle
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.generation.schemas.generation_request import GenerationRequestCreate, GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobCreate, ImageGenerationJobUpdate
from app.domain.generation.models.image import GeneratedImage, GeneratedImageGroup
from app.domain.generation.schemas.generated_image import GeneratedImageCreate, GeneratedImageUpdate


class GenerationRequestRepository(CRUDRepository[GenerationRequest, GenerationRequestCreate, GenerationRequestUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GenerationRequest, db=db)

    def get_latest_generation_request_by_user(self, user_id: int) -> GenerationRequest:
        stmt = (
            select(GenerationRequest)
            .where(GenerationRequest.user_id == user_id)
            .order_by(GenerationRequest.updated_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_with_all_relations(self, generation_request_id: int) -> GenerationRequest:
       stmt = (
           select(GenerationRequest)
           .options(
               joinedload(GenerationRequest.hair_variant_model).options(
                   joinedload(HairVariantModel.gender),
                   joinedload(HairVariantModel.hair_style).options(
                       joinedload(HairStyle.length)
                   ),
                   joinedload(HairVariantModel.length),
                   joinedload(HairVariantModel.color),
                   joinedload(HairVariantModel.lora_model)
               ),
               joinedload(GenerationRequest.background),
               joinedload(GenerationRequest.image_resolution)
           )
           .where(GenerationRequest.id == generation_request_id)
       )
       return self.db.scalars(stmt).first()

def get_generation_request_repository(db: Session = Depends(get_db)) -> GenerationRequestRepository:
    return GenerationRequestRepository(db=db)

class ImageGenerationJobRepository(CRUDRepository[ImageGenerationJob, ImageGenerationJobCreate, ImageGenerationJobUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageGenerationJob, db=db)

    def get_all_by_generation_request(self, generation_request_id: int) -> List[ImageGenerationJob]:
        stmt = select(ImageGenerationJob).where(ImageGenerationJob.generation_request_id == generation_request_id)
        return list(self.db.scalars(stmt).all())

    def get_all_expired_but_to_process_jobs(self) -> List[ImageGenerationJob]:
        stmt = select(ImageGenerationJob).where(
            and_(
                # 아직 처리 중인 작업
                ImageGenerationJob.status.in_([GenerationStatusEnum.PENDING, GenerationStatusEnum.PROCESSING]),
                ImageGenerationJob.expires_at < datetime.now(UTC),  # 만료된 작업
            )
        ).order_by(ImageGenerationJob.created_at)
        return list(self.db.scalars(stmt).all())

def get_image_generation_job_repository(db: Session = Depends(get_db)) -> ImageGenerationJobRepository:
    return ImageGenerationJobRepository(db=db)

class GeneratedImageRepository(CRUDRepository[GeneratedImage, GeneratedImageCreate, GeneratedImageUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImage, db=db)

    def get_all_by_generate_image_group(self, generated_image_group_id: int) -> List[GeneratedImage]:
        stmt = select(GeneratedImage).where(
            GeneratedImage.generated_image_group_id == generated_image_group_id,
            GeneratedImage.deleted == False
        )
        return list(self.db.scalars(stmt).all())

    def soft_delete_all_in(self, id_list: List[int]) -> bool:
        stmt = update(GeneratedImage).where(GeneratedImage.id.in_(id_list)).values(deleted=True)
        self.db.execute(stmt)
        self.db.commit()
        return True


def get_generated_image_repository(db: Session = Depends(get_db)) -> GeneratedImageRepository:
    return GeneratedImageRepository(db=db)

class GeneratedImageGroupRepository(CRUDRepository[GeneratedImageGroup, GeneratedImageGroupCreate, GeneratedImageGroupUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GeneratedImageGroup, db=db)

    def get_all_by_user(self, user_id: int) -> List[GeneratedImageGroup]:
        stmt = select(GeneratedImageGroup).where(
            GeneratedImageGroup.user_id == user_id,
            GeneratedImageGroup.deleted == False
        )
        return list(self.db.scalars(stmt).all())

    def get_by_generation_request(self, generation_request_id: int) -> GeneratedImageGroup:
        stmt = select(GeneratedImageGroup).where(
            GeneratedImageGroup.generation_request_id == generation_request_id,
            GeneratedImageGroup.deleted == False
        )
        result = self.db.execute(stmt)
        return result.scalar_one()

    def soft_delete(self, generated_image_group_id: int) -> bool:
        stmt = update(GeneratedImageGroup).where(GeneratedImageGroup.id == generated_image_group_id).values(deleted=True)
        self.db.execute(stmt)
        self.db.commit()
        return True

def get_generated_image_group_repository(db: Session = Depends(get_db)) -> GeneratedImageGroupRepository:
    return GeneratedImageGroupRepository(db=db)
