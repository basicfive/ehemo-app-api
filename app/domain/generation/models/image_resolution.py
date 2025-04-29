from sqlalchemy import Column, String, Integer, ForeignKey, Boolean

from app.domain.time_stamp_model import TimeStampModel

class ImageRatio(TimeStampModel):
    __tablename__ = "image_ratio"
    title = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    thumbnail_s3_key = Column(String(2048), nullable=False)

    aspect_width = Column(Integer, nullable=False)
    aspect_height = Column(Integer, nullable=False)
    order = Column(Integer, nullable=True)

class ImageResolution(TimeStampModel):
    __tablename__ = "image_resolution"
    
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    is_high_resolution = Column(Boolean, nullable=False)

    image_ratio_id = Column(ForeignKey("image_ratio.id"), nullable=False)
