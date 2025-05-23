from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import List, Optional
from fastapi import Depends
from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.training.enums.training_status import TrainingJobStatus
from app.domain.training.models.training import TrainingRequest, TrainingJob
from app.domain.training.schemas.training.training_request import TrainingRequestCreate, TrainingRequestUpdate
from app.domain.training.schemas.training.training_job import TrainingJobCreate, TrainingJobUpdate
from app.domain.training.enums.training_status import TrainingRequestStatus

class TrainingRequestRepository(CRUDRepository[TrainingRequest, TrainingRequestCreate, TrainingRequestUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=TrainingRequest, db=db)
    
    def get_user_pending_request_or_none(self, user_id: int) -> Optional[TrainingRequest]:
        stmt = (
            select(TrainingRequest)
            .where(TrainingRequest.user_id == user_id)
            .where(TrainingRequest.status == TrainingRequestStatus.PENDING)
        )
        return self.db.execute(stmt).scalars().one_or_none()

    def get_with_user(self, training_request_id: int) -> TrainingRequest:
        stmt = (
            select(TrainingRequest)
            .options(joinedload(TrainingRequest.user))
            .where(TrainingRequest.id == training_request_id)
        )
        return self.db.execute(stmt).scalars().one()

def get_training_request_repository(db: Session = Depends(get_db)) -> TrainingRequestRepository:
    return TrainingRequestRepository(db=db)

class TrainingJobRepository(CRUDRepository[TrainingJob, TrainingJobCreate, TrainingJobUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=TrainingJob, db=db)
    
    def get_latest_training_job_by_user(self, user_id: int) -> Optional[TrainingJob]:
        stmt = (
            select(TrainingJob)
            .where(TrainingJob.user_id == user_id)
            .order_by(TrainingJob.requested_at.desc())
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalars().one_or_none()

    def get_pending_training_jobs(self) -> List[TrainingJob]:
        stmt = (
            select(TrainingJob)
            .where(TrainingJob.status == TrainingJobStatus.PENDING)
            .order_by(TrainingJob.requested_at.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_with_request_with_user(self, training_job_id: int) -> TrainingJob:
        stmt = (
            select(TrainingJob)
            .options(
                joinedload(TrainingJob.training_request).joinedload(TrainingRequest.user)
            )
            .where(TrainingJob.id == training_job_id)
        )
        result = self.db.execute(stmt)
        return result.scalars().one()


def get_training_job_repository(db: Session = Depends(get_db)) -> TrainingJobRepository:
    return TrainingJobRepository(db=db)
