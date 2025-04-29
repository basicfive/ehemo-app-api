from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.domain.common.enums.ai_status import TrainingJobStatus
from app.domain.common.enums.gender import Gender

class TrainingJobCreate(BaseModel):
    gender: Gender
    training_request_id: int
    status: TrainingJobStatus
    total_steps: int
    image_count: int
    epoch: int

    requested_at: datetime

class TrainingJobUpdate(BaseModel):
    status: Optional[TrainingJobStatus] = None
    actual_training_time_sec: Optional[int] = None
    response_at: Optional[datetime] = None

class TrainingJobInDB(BaseModel):
    id: int
    training_request_id: int
    gender: Gender
    status: TrainingJobStatus
    actual_training_time_sec: Optional[int] = None
    total_steps: int
    image_count: int
    epoch: int
    requested_at: Optional[datetime] = None
    response_at: Optional[datetime] = None

    class Config:
        from_attributes = True
