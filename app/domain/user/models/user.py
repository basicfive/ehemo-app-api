from sqlalchemy import Column, String, Integer, Index, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.db.time_stamp_model import TimeStampModel

class User(TimeStampModel):
    __tablename__ = "user"

    # UUID 필드 추가
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    token = Column(Integer, default=0, nullable=False)
    email = Column(String(320), nullable=False)
    provider = Column(String(20), nullable=False)
    social_id = Column(String(255), nullable=False)

    deleted = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index(
            'idx_provider_social_id_active',
            'provider',
            'social_id',
            unique=True,
            postgresql_where=text('deleted = false')
        ),
    )

    def has_enough_token(self) -> bool:
        if self.token == 0:
            return False
        return True
