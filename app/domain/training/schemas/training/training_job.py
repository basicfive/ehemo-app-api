from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.domain.training.enums.training_status import TrainingJobStatus
from app.domain.common.enums.gender import Gender

class TrainingJobCreate(BaseModel):
    expires_at: datetime
    gender: Gender
    training_request_id: int
    status: TrainingJobStatus
    total_steps: int
    image_count: int
    epoch: int

    requested_at: datetime
    thumbnail_s3_key: str
    thumbnail_width: int
    thumbnail_height: int
    thumbnail_prompt: str

class TrainingJobUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    status: Optional[TrainingJobStatus] = None
    actual_training_time_sec: Optional[int] = None
    response_at: Optional[datetime] = None
    thumbnail_creation_failure_count: Optional[int] = None
    thumbnail_creation_expires_at: Optional[datetime] = None

class TrainingJobInDB(BaseModel):
    id: int
    expires_at: datetime = None
    training_request_id: int
    gender: Gender
    status: TrainingJobStatus
    actual_training_time_sec: Optional[int] = None
    total_steps: int
    image_count: int
    epoch: int
    requested_at: Optional[datetime] = None
    response_at: Optional[datetime] = None

    thumbnail_creation_failure_count: Optional[int] = None
    thumbnail_creation_expires_at: Optional[datetime] = None

    thumbnail_s3_key: str
    thumbnail_width: int
    thumbnail_height: int
    thumbnail_prompt: str

    class Config:
        from_attributes = True
