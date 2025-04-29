from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.common.enums.gender import Gender

class HairStyleLora(TimeStampModel):
    __tablename__ = "hair_style_lora"

    lora_name = Column(String, nullable=False)
    lora_s3_key = Column(String, nullable=False)


class HairStyle(TimeStampModel):
    __tablename__ = "hair_style"

    order = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)

    thumbnail_s3_key = Column(String(2048), nullable=False) 
    title = Column(String(255), nullable=False)
    description = Column(String(100), nullable=False)

    hair_style_lora_id = Column(Integer, ForeignKey("hair_style_lora.id"), nullable=True)
    hair_style_lora = relationship("HairStyleLora")