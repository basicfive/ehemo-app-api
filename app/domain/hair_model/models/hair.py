from sqlalchemy import String, Column, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.db.time_stamp_model import TimeStampModel

class Gender(TimeStampModel):
    __tablename__ = "gender"
    title = Column(String(20), nullable=False)
    description = Column(String(100), nullable=False)
    prompt = Column(String(20), nullable=False)
    order = Column(Integer, nullable=False)
    image_s3_key = Column(String(2048), nullable=False)

class HairStyle(TimeStampModel):
    __tablename__ = "hair_style"
    title = Column(String(255), nullable=False)
    description = Column(String(100), nullable=False)
    image_s3_key = Column(String(2048), nullable=False)
    has_length_option = Column(Boolean, nullable=False)
    order = Column(Integer, nullable=False)
    # has_bangs_option = Column(Boolean, nullable=False)

    gender_id = Column(Integer, ForeignKey("gender.id"), nullable=False, index=True)
    length_id = Column(Integer, ForeignKey("length.id"), nullable=True)
    # bangs_id = Column(Integer, nullable=True)

class Length(TimeStampModel):
    __tablename__ = "length"
    title = Column(String(255), nullable=False)
    description = Column(String(100), nullable=False)
    prompt = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False)

# class Bangs(TimeStampModel):
#     __tablename__ = "bangs"
#     name = Column(String(255), nullable=False)
#     prompt = Column(String(255), nullable=False)

class SpecificColor(TimeStampModel):
    __tablename__ = "specific_color"
    prompt = Column(String(255), nullable=False)

    color_id = Column(Integer, ForeignKey("color.id"), nullable=False, index=True)

class Color(TimeStampModel):
    __tablename__ = "color"
    title = Column(String(255), nullable=False)
    description = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)

class LoRAModel(TimeStampModel):
    __tablename__ = "lora_model"
    prompt = Column(String(255), nullable=False)
    lora_model_description = Column(String(255), nullable=True)
    supported_style = Column(String(255), nullable=True)
    supported_lengths = Column(String(255), nullable=True)
    supported_colors = Column(String(255), nullable=True)

class HairStyleLength(TimeStampModel):
    __tablename__ = "hair_style_length"
    image_s3_key = Column(String(2048), nullable=False)

    hair_style_id = Column(Integer, ForeignKey("hair_style.id"), nullable=False, index=True)
    length_id = Column(Integer, ForeignKey("length.id"), nullable=False)

    hair_style = relationship("HairStyle")
    length = relationship("Length")

# class HairStyleBang(TimeStampModel):
#     __tablename__ = "hair_style_bang"
#     # image_s3_key = Column(String(2048), nullable=False)

#     hair_style_id = Column(Integer, nullable=False)
#     bangs_id = Column(Integer, nullable=False)

class HairDesign(TimeStampModel):
    __tablename__ = "hair_design"

    hair_style_id = Column(Integer, ForeignKey("hair_style.id"), nullable=False, index=True)
    length_id = Column(Integer, ForeignKey("length.id"), nullable=True)
    # bangs_id = Column(Integer, nullable=True)

class HairDesignColor(TimeStampModel): # HairDesignColor == HairVariant
    __tablename__ = "hair_design_color"
    image_s3_key = Column(String(2048), nullable=False)

    hair_design_id = Column(Integer, ForeignKey("hair_design.id"), nullable=False, index=True)
    color_id = Column(Integer, ForeignKey("color.id"), nullable=False)

    color = relationship("Color")

class HairVariantModel(TimeStampModel):
    __tablename__ = "hair_variant_model"

    gender_id = Column(Integer, ForeignKey("gender.id"), nullable=False)
    hair_style_id = Column(Integer, ForeignKey("hair_style.id"), nullable=False)
    length_id = Column(Integer, ForeignKey("length.id"), nullable=True)
    color_id = Column(Integer, ForeignKey("color.id"), nullable=False)
    lora_model_id = Column(Integer, ForeignKey("lora_model.id"), nullable=False)

    __table_args__ = (
        Index('idx_hair_variant_style_length_color',
              'hair_style_id', 'length_id', 'color_id'),
    )

