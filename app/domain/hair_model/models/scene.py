from sqlalchemy import Column, String, Integer, ForeignKey

from app.core.db.time_stamp_model import TimeStampModel

class Background(TimeStampModel):
    __tablename__ = "background"
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    prompt = Column(String(1024), nullable=False)
    image_s3_key = Column(String(2048), nullable=False)

class PostureAndClothing(TimeStampModel):
    __tablename__ = "posture_and_clothing"
    prompt = Column(String(1024), nullable=False)

    gender_id = Column(Integer, ForeignKey("gender.id"), index=True)


class ImageResolution(TimeStampModel):
    __tablename__ = "image_resolution"
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    aspect_width = Column(Integer, nullable=False)
    aspect_height = Column(Integer, nullable=False)
    image_s3_key = Column(String(2048), nullable=False)
