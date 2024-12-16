from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.config import timezone_config
from app.core.db.time_stamp_model import TimeStampModel
from app.domain.subscription.models.enums.subscription import SubscriptionStatus, SubscriptionPlanType, BillingInterval, StoreType


class Subscription(TimeStampModel):
    __tablename__ = "subscription"
    original_transaction_id = Column(String(50), unique=True, nullable=True, index=True)
    store = Column(Enum(StoreType), nullable=True)

    token = Column(Integer, nullable=False)
    timezone = Column(String, nullable=False, default=timezone_config.UTC)
    next_token_refill_date = Column(DateTime(timezone=True), nullable=False)
    expire_date = Column(DateTime(timezone=True), nullable=False)

    plan_type = Column(Enum(SubscriptionPlanType), nullable=False)
    billing_interval = Column(Enum(BillingInterval), nullable=True)
    status = Column(Enum(SubscriptionStatus), nullable=False)

    user_id = Column(ForeignKey("user.id"), unique=True, nullable=False, index=True)

    user = relationship("User", back_populates="subscription")

    def has_available_token(self) -> bool:
        return self.token > 0
