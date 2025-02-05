from sqlalchemy import Column, String, Integer, ForeignKey, Boolean

from app.domain.time_stamp_model import TimeStampModel

class Background(TimeStampModel):
    __tablename__ = "background"
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    prompt = Column(String(1024), nullable=False)
    image_s3_key = Column(String(2048), nullable=False)
    order = Column(Integer, nullable=True)

class PostureAndClothing(TimeStampModel):
    __tablename__ = "posture_and_clothing"
    prompt = Column(String(1024), nullable=False)

    gender_id = Column(Integer, ForeignKey("gender.id"), index=True)

class ImageRatio(TimeStampModel):
    __tablename__ = "image_ratio"
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    aspect_width = Column(Integer, nullable=False)
    aspect_height = Column(Integer, nullable=False)
    image_s3_key = Column(String(2048), nullable=False)
    order = Column(Integer, nullable=True)

class ImageResolution(TimeStampModel):
    __tablename__ = "image_resolution"
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    aspect_width = Column(Integer, nullable=False) # TODO: delete
    aspect_height = Column(Integer, nullable=False) # TODO: delete
    image_s3_key = Column(String(2048), nullable=False)
    order = Column(Integer, nullable=True) # TODO: not nullable
    is_upscale = Column(Boolean, nullable=True) # TODO: not nullable

    image_ratio_id = Column(ForeignKey("image_ratio.id"), nullable=True) # TODO: not nullable
