from sqlalchemy import Column, String, Integer, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.generation.models.enums.generation_status import GenerationStatusEnum, GenerationResultEnum
from app.domain.time_stamp_model import TimeStampModel

class GenerationRequest(TimeStampModel):
    __tablename__ = "generation_request"
    generation_result = Column(Enum(GenerationResultEnum), default=GenerationResultEnum.PENDING, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    hair_variant_model_id = Column(Integer, ForeignKey("hair_variant_model.id"))
    background_id = Column(Integer, ForeignKey("background.id"))
    image_resolution_id = Column(Integer, ForeignKey("image_resolution.id"))

    hair_variant_model = relationship("HairVariantModel")
    background = relationship("Background")
    image_resolution = relationship("ImageResolution")

class ImageGenerationJob(TimeStampModel):
    __tablename__ = "image_generation_job"
    status = Column(Enum(GenerationStatusEnum), default=GenerationStatusEnum.PENDING, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    s3_key = Column(String(1024), nullable=False)
    webui_png_info = Column(String(2048), nullable=True)

    prompt = Column(String(1024), nullable=False)
    distilled_cfg_scale = Column(Float, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    generation_request_id = Column(Integer, ForeignKey("generation_request.id"), index=True)
