from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.domain.training.enums.training_status import TrainingRequestStatus
from app.domain.common.enums.gender import Gender

class TrainingRequestCreate(BaseModel):
    user_id: int
    gender: Gender
    title: str
    description: str
    status: TrainingRequestStatus

class TrainingRequestUpdate(BaseModel):
    status: Optional[TrainingRequestStatus] = None

class TrainingRequestInDB(BaseModel):
    id: int
    user_id: int
    gender: Gender
    title: str
    description: str
    status: TrainingRequestStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True