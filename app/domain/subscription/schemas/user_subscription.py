from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.domain.subscription.models.enums.subscription import StoreType, SubscriptionPlanType, BillingInterval, SubscriptionStatus


class UserSubscriptionCreate(BaseModel):
    original_transaction_id: str
    latest_transaction_id: str
    purchase_date: datetime
    expire_date: datetime

    status: SubscriptionStatus
    auto_renew_status: bool

    user_id: int
    subscription_plan_id: int

class UserSubscriptionUpdate(BaseModel):
    original_transaction_id: Optional[str] = None
    last_transaction_id: Optional[str] = None
    purchase_date: Optional[datetime] = None
    expire_date: Optional[datetime] = None

    status: Optional[SubscriptionStatus] = None
    auto_renew_status: Optional[bool] = None

    user_id: Optional[int] = None
    subscription_plan_id: Optional[int] = None

class UserSubscriptionInDB(BaseModel):
    id: int
    original_transaction_id: str
    latest_transaction_id: Optional[str]
    purchase_date: datetime
    expire_date: datetime

    status: SubscriptionStatus
    auto_renew_status: bool

    user_id: int
    subscription_plan_id: int

    class Config:
        from_attributes=True