from sqlalchemy import Column, String, Integer

from app.models.base import TimeStampModel

class User(TimeStampModel):
    __tablename__ = "user"
    email = Column(String(50), nullable=False, index=True)
    token = Column(Integer, default=0, nullable=False)

