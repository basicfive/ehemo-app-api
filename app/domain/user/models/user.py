from sqlalchemy import Column, String, Index, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.domain.time_stamp_model import TimeStampModel

class User(TimeStampModel):
    __tablename__ = "user"

    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    fcm_token = Column(String(255), nullable=True)

    email = Column(String(320), nullable=False)
    provider = Column(String(20), nullable=False)
    social_id = Column(String(255), nullable=False)

    deleted = Column(Boolean, default=False, nullable=False)
    timezone = Column(String(20), nullable=True)

    user_subscriptions = relationship("UserSubscription", back_populates="user", uselist=True)
    token_wallets = relationship("TokenWallet", back_populates="user", uselist=True)

    __table_args__ = (
        Index(
            'idx_provider_social_id_active',
            'provider',
            'social_id',
            unique=True,
            postgresql_where=text('deleted = false')
        ),
    )

    @property
    def current_subscription(self):
        """
        is_current = True 인 구독을 찾아서 반환.
        없으면 None.
        """
        return next((sub for sub in self.user_subscriptions if sub.is_current), None)

    @property
    def current_token_wallet(self):
        """
        is_current = True 인 구독을 찾아서 반환.
        없으면 None.
        """
        return next((wallet for wallet in self.token_wallets if wallet.is_current), None)