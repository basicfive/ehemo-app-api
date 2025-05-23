from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel


class UploadedImageForTraining(TimeStampModel):
    __tablename__ = "uploaded_image_for_training"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    s3_key = Column(String, nullable=False)

    training_request_id = Column(Integer, ForeignKey("training_request.id"), index=True)
    training_request = relationship("TrainingRequest")
