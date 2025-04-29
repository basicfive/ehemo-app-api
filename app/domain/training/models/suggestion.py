from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel


class UserHairStyleTitleSuggestion(TimeStampModel):
    __tablename__ = "user_hair_style_title_suggestion"

    title = Column(String, nullable=False)

class UserHairStyleDescriptionSuggestion(TimeStampModel):
    __tablename__ = "user_hair_style_description_suggestion"

    description = Column(String, nullable=False)

