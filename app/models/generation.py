from sqlalchemy import Column, String, Integer, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.enums.generation_status import GenerationStatusEnum
from app.models.base import TimeStampModel

class GenerationRequest(TimeStampModel):
    __tablename__ = "generation_request"

    user_id = Column(Integer, index=True)
    hair_variant_model_id = Column(Integer)
    background_id = Column(Integer)
    image_resolution_id = Column(Integer)

    user = relationship("User", back_populates="generation_request")
    hair_variant_model = relationship("HairVariantModel", back_populates="generation_request")
    background = relationship("Background", back_populates="generation_request")
    image_resolution = relationship("ImageResolution", back_populates="generation_request")
    image_generation_job = relationship("ImageGenerationJob", back_populates="generation_request")

class ImageGenerationJob(TimeStampModel):
    __tablename__ = "image_generation_job"
    status = Column(Enum(GenerationStatusEnum), default=GenerationStatusEnum.PENDING, nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    prompt = Column(String(1024), nullable=False)
    distilled_cfg_scale = Column(Float, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    generation_request_id = Column(Integer, index=True)

    generation_request = relationship("GenerationRequest", back_populates="image_generation_job.py")
    generated_image = relationship("GeneratedImage", back_populates="image_generation_job.py")
