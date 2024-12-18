from sqlalchemy import Column, String, Integer, ForeignKey, Boolean

from app.domain.time_stamp_model import TimeStampModel

class GeneratedImage(TimeStampModel):
    __tablename__ = "generated_image"
    s3_key = Column(String(1024), nullable=False)
    webui_png_info = Column(String(2048), nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    generated_image_group_id = Column(Integer, ForeignKey("generated_image_group.id"), index=True)
    image_generation_job_id = Column(Integer, ForeignKey("image_generation_job.id"))

class GeneratedImageGroup(TimeStampModel):
    __tablename__ = "generated_image_group"

    title = Column(String(100), nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    thumbnail_image_s3_key = Column(String(2048), nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    generation_request_id = Column(Integer, ForeignKey("generation_request.id"), index=True)


class ExampleGeneratedImage(TimeStampModel):
    __tablename__ = "example_generated_image"
    s3_key = Column(String(1024), nullable=False)
    webui_png_info = Column(String(2048), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)

    example_generated_image_group_id = Column(Integer, ForeignKey("example_generated_image_group.id"), index=True)

class ExampleGeneratedImageGroup(TimeStampModel):
    __tablename__ = "example_generated_image_group"

    title = Column(String(100), nullable=False)
    rating = Column(Integer, default=0, nullable=False)
    thumbnail_image_s3_key = Column(String(2048), nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
