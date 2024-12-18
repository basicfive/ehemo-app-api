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

# class SubPlanInfo(BaseModel):
#     id: int
#     name: str
#     description: str
#
#     plan_type: SubscriptionPlanType
#     billing_interval: Optional[BillingInterval]
#
#     tokens_per_period: int
#
#     base_price: float
#     discount_rate: float
#     final_price: float
#
#     has_discount: bool
#     discount_description: Optional[str]
#
#     store_type: Optional[StoreType]
#     product_id: Optional[int]
#

