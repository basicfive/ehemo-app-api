from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.common.enums.gender import Gender
from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus

class UserHairStyleLora(TimeStampModel):
    __tablename__ = "user_hair_style_lora"

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    training_request_id = Column(Integer, ForeignKey("training_request.id"), index=True)
    training_request = relationship("TrainingRequest")

    lora_name = Column(String, nullable=False)
    lora_s3_key = Column(String, nullable=False)


class UserHairStyle(TimeStampModel):
    __tablename__ = "user_hair_style"

    status = Column(Enum(UserHairStyleStatus), default=UserHairStyleStatus.PENDING, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User")

    order = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)

    thumbnail_s3_key = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    user_hair_style_lora_id = Column(Integer, ForeignKey("user_hair_style_lora.id"), nullable=True)
    user_hair_style_lora = relationship("UserHairStyleLora")
