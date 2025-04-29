from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel


class UploadedImagesForTraining(TimeStampModel):
    __tablename__ = "uploaded_images_for_training"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    s3_key = Column(String, nullable=False)


class TrainingRequestUploadedImages(TimeStampModel):
    __tablename__ = "training_request_uploaded_images"

    training_request_id = Column(Integer, ForeignKey("training_request.id"), index=True)
    training_request = relationship("TrainingRequest")

    uploaded_images_for_training_id = Column(Integer, ForeignKey("uploaded_images_for_training.id"), index=True)
    uploaded_images_for_training = relationship("UploadedImagesForTraining")

    