from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, Index
from app.core.db.time_stamp_model import TimeStampModel

class User(TimeStampModel):
    __tablename__ = "user"

    token = Column(Integer, default=0, nullable=False)
    email = Column(String(320), nullable=False)
    provider = Column(String(20), nullable=False)
    social_id = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint('provider', 'social_id', name='uix_provider_social_id'),
        Index('idx_provider_social_id', 'provider', 'social_id'),
    )

    def has_enough_token(self) -> bool:
        if self.token == 0:
            return False
        return True
