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
    initial_purchase_date = Column(DateTime, nullable=True)
    purchase_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime, nullable=False)

    # 구독 상태
    is_current = Column(Boolean, nullable=True)
    status = Column(Enum(SubscriptionStatus), nullable=False, index=True)

    user_id = Column(ForeignKey("user.id"), nullable=False, index=True)
    subscription_plan_id = Column(ForeignKey("subscription_plan.id"), nullable=False, index=True)

    user = relationship("User", back_populates="user_subscriptions")
    subscription_plan = relationship("SubscriptionPlan", back_populates="user_subscription")

    token_wallet = relationship("TokenWallet", back_populates="user_subscription", uselist=False)

    __table_args__ = (
        # 1) is_current = TRUE 일 때만 original_transaction_id 유니크
        Index(
            "uq_current_original_transaction",
            "original_transaction_id",
            unique=True,
            postgresql_where=text("is_current = TRUE"),
        ),
        # # 2) is_current = TRUE 일 때만 user_id 유니크
        # Index(
        #     "uq_current_user",
        #     "user_id",
        #     unique=True,
        #     postgresql_where=text("is_current = TRUE"),
        # ),
        # status, expire_date로 만든 일반 인덱스
        Index("idx_subscription_status_expire", "status", "expire_date"),
    )

