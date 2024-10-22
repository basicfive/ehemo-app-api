from sqlalchemy import Column, String, Integer, ForeignKey

from app.core.db.time_stamp_model import TimeStampModel

class GeneratedImage(TimeStampModel):
    __tablename__ = "generated_image"
    s3_key = Column(String(1024), nullable=False)
    webui_png_info = Column(String(2048), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    generated_image_group_id = Column(Integer, ForeignKey("generated_image_group.id"), index=True)
    image_generation_job_id = Column(Integer, ForeignKey("image_generation_job.id"))

class GeneratedImageGroup(TimeStampModel):
    __tablename__ = "generated_image_group"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    generation_request_id = Column(Integer, ForeignKey("generation_request.id"), index=True)


