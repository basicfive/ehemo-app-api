from sqlalchemy import Column, String, Integer, DateTime, Float, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.domain.generation.enums.generation_status import GenerationJobStatus, GenerationRequestResult
from app.domain.generation.enums.reference_image_similarity import ReferenceImageSimilarity
from app.domain.time_stamp_model import TimeStampModel

class GenerationRequest(TimeStampModel):
    __tablename__ = "generation_request"

    request_number = Column(String(20), nullable=False)
    result = Column(Enum(GenerationRequestResult), default=GenerationRequestResult.PENDING, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)

    is_user_hair_style = Column(Boolean, default=False, nullable=False)

    hair_style_id = Column(Integer, ForeignKey("hair_style.id"), nullable=True)
    hair_style = relationship("HairStyle")

    user_hair_style_id = Column(Integer, ForeignKey("user_hair_style.id"), nullable=True)
    user_hair_style = relationship("UserHairStyle")

    # 이미지 화질
    image_resolution_id = Column(Integer, ForeignKey("image_resolution.id"))
    image_resolution = relationship("ImageResolution")

    # img2img 이미지
    is_user_reference_image = Column(Boolean, default=False, nullable=False)
    user_reference_image_s3_key = Column(String(2048), nullable=True)
    user_reference_image_similarity = Column(Enum(ReferenceImageSimilarity), nullable=True)

    # 완성된 프롬프트
    final_generation_prompt = Column(String(1024), nullable=False)

    # 토큰
    consumed_tokens = Column(Integer, nullable=False)

    is_favorite = Column(Boolean, default=False, nullable=False)

    generation_job = relationship("GenerationJob", back_populates="generation_request", uselist=False)

class GenerationJob(TimeStampModel):
    __tablename__ = "generation_job"
    status = Column(Enum(GenerationJobStatus), default=GenerationJobStatus.PENDING, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    image_count = Column(Integer, default=1, nullable=False)

    prompt = Column(String(1024), nullable=False)

    is_user_hair_style = Column(Boolean, nullable=False)
    user_hair_lora_model_s3_key = Column(String(1024), nullable=True)
    hair_lora_model_name = Column(String(1024), nullable=False)

    distilled_cfg_scale = Column(Float, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)

    is_user_reference_image = Column(Boolean, nullable=False)
    user_reference_image_s3_key = Column(String(1024), nullable=True)
    user_reference_image_denoise_strength = Column(Float, nullable=True)

    generation_request_id = Column(Integer, ForeignKey("generation_request.id"), index=True, nullable=True)
    generation_request = relationship("GenerationRequest", back_populates="generation_job")

class RequestPromptComponentQuestionAnswer(TimeStampModel):
    __tablename__ = "request_prompt_component_question_answer"

    generation_request_id = Column(Integer, ForeignKey("generation_request.id"), index=True)
    generation_request = relationship("GenerationRequest")

    prompt_component_question_id = Column(Integer, ForeignKey("prompt_component_question.id"), nullable=False)
    prompt_component_question = relationship("PromptComponentQuestion")

    answer = Column(String(200), nullable=False)