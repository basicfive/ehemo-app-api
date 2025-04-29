from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.generation.enums.generated_image_status import GeneratedImageStatus

class GeneratedImage(TimeStampModel):
    __tablename__ = "generated_image"

    status = Column(Enum(GeneratedImageStatus), default=GeneratedImageStatus.PENDING, nullable=False)

    s3_key = Column(String(1024), nullable=True)
    upscaled_s3_key = Column(String(1024), nullable=True)

    webui_png_info = Column(String(2048), nullable=True)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    generation_job_id = Column(Integer, ForeignKey("generation_job.id"))
    generation_job = relationship("GenerationJob")