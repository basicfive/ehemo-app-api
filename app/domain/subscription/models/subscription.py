from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Float, Boolean, UniqueConstraint, Index, text
from sqlalchemy.orm import relationship

from app.domain.time_stamp_model import TimeStampModel
from app.domain.subscription.models.enums.subscription import SubscriptionStatus, SubscriptionPlanType, BillingInterval, \
    StoreType, Currency


class SubscriptionPlan(TimeStampModel):
    __tablename__ = "subscription_plan"
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    plan_type = Column(Enum(SubscriptionPlanType), nullable=False)
    billing_interval = Column(Enum(BillingInterval), nullable=True)

    tokens_per_period = Column(Integer, nullable=False)

    base_price = Column(Float, nullable=False)
    discount_rate = Column(Float, default=0.0, nullable=False)
    final_price = Column(Float, nullable=False)

    has_discount = Column(Boolean, default=False, nullable=False)
    discount_description = Column(String)

    store_type = Column(Enum(StoreType), nullable=False)
    product_id = Column(String, nullable=True)

    user_subscription = relationship("UserSubscription", back_populates="subscription_plan")


class UserSubscription(TimeStampModel):
    __tablename__ = "user_subscription"
    # RevenueCat 관련 정보
    original_transaction_id = Column(String(50), nullable=False, index=True)
    latest_transaction_id = Column(String(50))
    purchase_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime, nullable=False)

    # 구독 상태
    status = Column(Enum(SubscriptionStatus), nullable=False, index=True)
    auto_renew_status = Column(Boolean, default=True, nullable=False)
    canceled_at = Column(DateTime, nullable=True)

    # 현재 사용자와 연결된 구독
    is_current_subscription = Column(Boolean, nullable=True) # nullable=False 로 전환할 것.

    user_id = Column(ForeignKey("user.id"), nullable=False, index=True)
    subscription_plan_id = Column(ForeignKey("subscription_plan.id"), nullable=False, index=True)

    user = relationship("User", back_populates="user_subscription")
    subscription_plan = relationship("SubscriptionPlan", back_populates="user_subscription")

    token_wallet = relationship("TokenWallet", back_populates="user_subscription", uselist=False)

    __table_args__ = (
        # 한 유저는 활성 구독을 하나만 가질 수 있도록 제약
        UniqueConstraint(
            'original_transaction_id',
            'user_id',
            'is_current_subscription',
            name='uq_user_original_transaction_current',
            deferrable=True,
            initially='DEFERRED',
            info=dict(where=text("is_current_subscription"))
        ),
        Index('idx_subscription_status_expire', 'status', 'expire_date'),
    )

