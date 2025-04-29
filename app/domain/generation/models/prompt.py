from sqlalchemy import String, Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.generation.enums.prompt_component import PromptComponentType

from app.domain.time_stamp_model import TimeStampModel
from app.domain.common.enums.gender import Gender


class PromptComponentQuestion(TimeStampModel):
    __tablename__ = "prompt_component_question"
    component_type = Column(Enum(PromptComponentType), nullable=False)
    title = Column(String(255), nullable=False)
    question = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)

    suggestions = relationship("PromptComponentSuggestion", back_populates="question")

class PromptComponentSuggestion(TimeStampModel):
    __tablename__ = "prompt_component_suggestion"
    suggestion = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)

    question_id = Column(Integer, ForeignKey("prompt_component_question.id"), nullable=False)
    question = relationship("PromptComponentQuestion", back_populates="suggestions")

class LengthPromptEnhancement(TimeStampModel):
    __tablename__ = "length_prompt_enhancement"
    gender = Column(Enum(Gender), nullable=False)
    keyword = Column(String(255), nullable=False)
    enhance_prompt = Column(String(255), nullable=False)

class ClothingPromptExample(TimeStampModel):
    __tablename__ = "clothing_prompt_example"
    gender = Column(Enum(Gender), nullable=False)
    prompt = Column(String(255), nullable=False)

class PosePromptExample(TimeStampModel):
    __tablename__ = "pose_prompt_example"
    prompt = Column(String(255), nullable=False)




