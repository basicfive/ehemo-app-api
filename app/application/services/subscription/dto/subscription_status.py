from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from app.domain.subscription.models.enums.subscription import SubscriptionPlanType, BillingInterval, StoreType

class UserSubscriptionInfo(BaseModel):
    original_transaction_id: str

    plan_type: SubscriptionPlanType
    name: str
    description: str

    next_billing_date: datetime

class UserSubscriptionStatus(BaseModel):
    is_subscribed: bool
    info: Optional[UserSubscriptionInfo] = None

