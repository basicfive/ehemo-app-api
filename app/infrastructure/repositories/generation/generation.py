from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_
from datetime import datetime, UTC

from typing import List

from app.core.db.base import get_db
from app.domain.generation.enums.generation_status import GenerationJobStatus
from app.domain.generation.models.generation import GenerationRequest, GenerationJob
from app.domain.generation.schemas.generation.generation_request import GenerationRequestCreate, GenerationRequestUpdate
from app.domain.generation.schemas.generation.generation_job import GenerationJobCreate, GenerationJobUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.generation.models.generation import RequestPromptComponentQuestionAnswer
from app.domain.generation.schemas.generation.request_prompt_component_question_answer import RequestPromptComponentQuestionAnswerCreate, RequestPromptComponentQuestionAnswerUpdate

class GenerationRequestRepository(CRUDRepository[GenerationRequest, GenerationRequestCreate, GenerationRequestUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GenerationRequest, db=db)
    
    def get_all_by_user_with_hair_style(self, user_id: int) -> List[GenerationRequest]:
        stmt = (
            select(GenerationRequest)
            .where(GenerationRequest.user_id == user_id)
            .options(joinedload(GenerationRequest.hair_style))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_by_request_number(self, request_number: str) -> GenerationRequest:
        stmt = select(GenerationRequest).where(GenerationRequest.request_number == request_number)
        result = self.db.execute(stmt)
        return result.scalars().one_or_none()
    
    def get_with_resolution(self, generation_request_id: int) -> GenerationRequest:
        stmt = (
            select(GenerationRequest).where(GenerationRequest.id == generation_request_id)
            .options(joinedload(GenerationRequest.image_resolution))
        )
        result = self.db.execute(stmt)
        return result.scalars().one()

    def get_with_relations(self, generation_request_id: int) -> GenerationRequest:
        stmt = (
            select(GenerationRequest).where(GenerationRequest.id == generation_request_id)
            .options(
                joinedload(GenerationRequest.image_resolution),
                joinedload(GenerationRequest.hair_style),
                joinedload(GenerationRequest.user_hair_style),
            )
        )
        result = self.db.execute(stmt)
        return result.scalars().one()

def get_generation_request_repository(db: Session = Depends(get_db)) -> GenerationRequestRepository:
    return GenerationRequestRepository(db=db)

class GenerationJobRepository(CRUDRepository[GenerationJob, GenerationJobCreate, GenerationJobUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=GenerationJob, db=db)
    
    def get_all_in_generation_requests(self, generation_request_ids: List[int]) -> List[GenerationJob]:
        stmt = (
            select(GenerationJob).where(GenerationJob.generation_request_id.in_(generation_request_ids))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_generation_request(self, generation_request_id: int) -> GenerationJob:
        stmt = select(GenerationJob).where(GenerationJob.generation_request_id == generation_request_id)
        result = self.db.execute(stmt)
        return result.scalars().one()

    def get_all_expired_but_to_process_jobs(self) -> List[GenerationJob]:
        stmt = (
            select(GenerationJob)
            .where(
                and_(
                    GenerationJob.status != GenerationJobStatus.COMPLETED,
                    GenerationJob.status != GenerationJobStatus.FAILED
                )
            )
            .where(GenerationJob.expires_at < datetime.now(UTC))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_pending_jobs_with_resolution(self) -> List[GenerationJob]:
        stmt = (
            select(GenerationJob)
            .filter(GenerationJob.status == GenerationJobStatus.PENDING)
            .options(
                joinedload(GenerationJob.generation_request)
                .joinedload(GenerationRequest.image_resolution)
            )
        )
        result = self.db.execute(stmt)
        return list(result.unique().scalars().all())

    def get_pending_upscale_jobs(self) -> List[GenerationJob]:
        stmt = (
            select(GenerationJob)
            .filter(GenerationJob.status == GenerationJobStatus.PENDING_UPSCALE)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

def get_generation_job_repository(db: Session = Depends(get_db)) -> GenerationJobRepository:
    return GenerationJobRepository(db=db)


class RequestPromptComponentQuestionAnswerRepository(CRUDRepository[RequestPromptComponentQuestionAnswer, RequestPromptComponentQuestionAnswerCreate, RequestPromptComponentQuestionAnswerUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=RequestPromptComponentQuestionAnswer, db=db)
    
    def get_all_by_generation_request_with_question(self, generation_request_id: int) -> List[RequestPromptComponentQuestionAnswer]:
        stmt = (
            select(RequestPromptComponentQuestionAnswer).where(RequestPromptComponentQuestionAnswer.generation_request_id == generation_request_id)
            .options(joinedload(RequestPromptComponentQuestionAnswer.prompt_component_question))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_all_in_generation_requests(self, generation_request_ids: List[int]) -> List[RequestPromptComponentQuestionAnswer]:
        stmt = (
            select(RequestPromptComponentQuestionAnswer).where(RequestPromptComponentQuestionAnswer.generation_request_id.in_(generation_request_ids))
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

def get_request_prompt_component_question_answer_repository(db: Session = Depends(get_db)) -> RequestPromptComponentQuestionAnswerRepository:
    return RequestPromptComponentQuestionAnswerRepository(db=db)

