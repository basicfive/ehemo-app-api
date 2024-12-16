from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.domain.subscription.models.enums.subscription import StoreType, SubscriptionPlanType, BillingInterval, SubscriptionStatus


class SubscriptionCreate(BaseModel):
    original_transaction_id: str
    store: Optional[StoreType]

    token: int
    timezone: str
    next_token_refill_date: datetime
    expire_date: datetime

    plan_type: SubscriptionPlanType
    billing_interval: Optional[BillingInterval]
    subscription_status: SubscriptionStatus

    user_id: int

class SubscriptionUpdate(BaseModel):
    token: Optional[int] = None
    timezone: Optional[str] = None
    next_token_refill_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None

    billing_interval: Optional[BillingInterval] = None
    subscription_status: Optional[SubscriptionStatus] = None

    user_id: Optional[int] = None

class SubscriptionInDB(BaseModel):
    original_transaction_id: str
    store: Optional[StoreType]

    token: int
    timezone: str
    next_token_refill_date: datetime
    expire_date: datetime

    plan_type: SubscriptionPlanType
    billing_interval: Optional[BillingInterval]
    subscription_status: SubscriptionStatus

    user_id: int

    class Config:
        from_attributes=True