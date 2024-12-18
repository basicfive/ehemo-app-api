from sqlalchemy import Column, String, ForeignKey, Integer

from app.domain.time_stamp_model import TimeStampModel

class ModelThumbnail(TimeStampModel):
    __tablename__ = "model_thumbnail"
    s3_key = Column(String(2048), nullable=False)
    order = Column(Integer, nullable=False)

    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)