from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from app.domain import SubscriptionStatus
from app.domain.subscription.models.enums.subscription import SubscriptionPlanType, BillingInterval, StoreType

class UserSubscriptionInfo(BaseModel):
    original_transaction_id: str
    subscription_plan_id: int

    plan_type: SubscriptionPlanType
    status: SubscriptionStatus
    name: str
    description: Optional[str]

    next_billing_date: datetime
    updated_at: datetime

class UserSubscriptionStatus(BaseModel):
    is_subscribed: bool
    info: Optional[UserSubscriptionInfo] = None

