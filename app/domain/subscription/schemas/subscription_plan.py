from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.domain.subscription.models.enums.subscription import BillingInterval, SubscriptionPlanType, StoreType


class SubscriptionPlanCreate(BaseModel):
    name: str
    description: str

    plan_type: SubscriptionPlanType
    billing_interval: Optional[BillingInterval]

    tokens_per_period: int

    base_price: float
    discount_rate: Optional[float]
    final_price: float

    has_discount: Optional[bool]
    discount_description: Optional[str]

    store_type: Optional[StoreType]
    product_id: Optional[str]


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    plan_type: Optional[SubscriptionPlanType] = None
    billing_interval: Optional[Optional[BillingInterval]] = None

    tokens_per_period: Optional[int] = None

    base_price: Optional[float] = None
    discount_rate: Optional[float]
    final_price: Optional[float] = None

    has_discount: Optional[bool] = None
    discount_description: Optional[str] = None

    store_type: Optional[StoreType] = None
    product_id: Optional[str] = None


class SubscriptionPlanInDB(BaseModel):
    id: int
    name: str
    description: str

    plan_type: SubscriptionPlanType
    billing_interval: Optional[BillingInterval]

    tokens_per_period: int

    base_price: float
    discount_rate: float
    final_price: float

    has_discount: bool
    discount_description: Optional[str]

    store_type: Optional[StoreType]
    product_id: Optional[str]

    class Config:
        from_attributes=True
