from typing import List
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db.base import get_db
from app.domain import ReasonOfDeletion, FollowUpAnswer, UserFollowUpAnswer, CustomReasonOfDeletion
from app.domain.user.schemas.deletion_survey import ReasonOfDeletionCreate, ReasonOfDeletionUpdate, \
    FollowUpAnswerCreate, FollowUpAnswerUpdate, UserFollowUpAnswerCreate, \
    UserFollowUpAnswerUpdate, CustomReasonOfDeletionCreate, CustomReasonOfDeletionUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository


class ReasonOfDeletionRepository(CRUDRepository[ReasonOfDeletion, ReasonOfDeletionCreate, ReasonOfDeletionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ReasonOfDeletion, db=db)
        self.db = db

def get_reason_of_deletion_repository(db: Session = Depends(get_db)):
    return ReasonOfDeletionRepository(db=db)

class CustomReasonOfDeletionRepository(CRUDRepository[CustomReasonOfDeletion, CustomReasonOfDeletionCreate, CustomReasonOfDeletionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=CustomReasonOfDeletion, db=db)
        self.db = db

def get_custom_reason_of_deletion_repository(db: Session = Depends(get_db)):
    return CustomReasonOfDeletionRepository(db=db)

class FollowUpAnswerRepository(CRUDRepository[FollowUpAnswer, FollowUpAnswerCreate, FollowUpAnswerUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=FollowUpAnswer, db=db)
        self.db = db

    def get_by_question(self, reason_id: int) -> List[FollowUpAnswer]:
        stmt = select(FollowUpAnswer).where(FollowUpAnswer.reason_id == reason_id)
        return list(self.db.scalars(stmt).all())

def get_follow_up_answer_repository(db: Session = Depends(get_db)):
    return FollowUpAnswerRepository(db=db)

class UserFollowUpAnswerRepository(CRUDRepository[UserFollowUpAnswer, UserFollowUpAnswerCreate, UserFollowUpAnswerUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserFollowUpAnswer, db=db)
        self.db = db

def get_user_follow_up_answer_repository(db: Session = Depends(get_db)):
    return UserFollowUpAnswerRepository(db=db)

