from sqlalchemy import Column, Integer, DateTime
from app.core.db.base import Base
from sqlalchemy.sql import func

class TimeStampModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
