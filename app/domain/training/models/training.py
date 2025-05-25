from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.training.enums.training_status import TrainingRequestStatus, TrainingJobStatus
from app.domain.common.enums.gender import Gender


class TrainingRequest(TimeStampModel):
    __tablename__ = "training_request"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    status = Column(Enum(TrainingRequestStatus), default=TrainingRequestStatus.PENDING, nullable=False)
    
    gender = Column(Enum(Gender), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)


class TrainingJob(TimeStampModel):
    __tablename__ = "training_job"

    training_request_id = Column(Integer, ForeignKey("training_request.id"), index=True)
    training_request = relationship("TrainingRequest")

    expires_at = Column(DateTime(timezone=True), nullable=False)

    gender = Column(Enum(Gender), nullable=False)

    total_steps = Column(Integer, nullable=False)
    image_count = Column(Integer, nullable=False)
    epoch = Column(Integer, nullable=False)

    actual_training_time_sec = Column(Integer, default=0, nullable=True)
    
    requested_at = Column(DateTime(timezone=True), nullable=True)
    response_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(Enum(TrainingJobStatus), default=TrainingJobStatus.PENDING, nullable=False)

    thumbnail_creation_failure_count = Column(Integer, default=0, nullable=False)
    thumbnail_creation_expires_at = Column(DateTime(timezone=True), nullable=True)

    thumbnail_s3_key = Column(String, nullable=True)
    thumbnail_width = Column(Integer, nullable=True)
    thumbnail_height = Column(Integer, nullable=True)
    thumbnail_prompt = Column(String, nullable=True)
