from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class EventType(str, Enum):
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    CANCELLATION = "CANCELLATION"
    UNCANCELLATION = "UNCANCELLATION"
    RENEWAL = "RENEWAL"
    PRODUCT_CHANGE = "PRODUCT_CHANGE"
    TEST = "TEST"

class SubscriberAttribute(BaseModel):
    updated_at_ms: int
    value: str


class BaseEvent(BaseModel):
    # 항상 존재하는 기본 이벤트 정보
    event_timestamp_ms: int
    environment: str
    type: EventType
    id: str
    app_id: str
    app_user_id: str
    original_app_user_id: str
    aliases: List[str]
    period_type: str
    product_id: str
    store: str

    # null이 올 수 있는 필드들
    entitlement_id: Optional[str]
    entitlement_ids: Optional[List[str]]
    presented_offering_id: Optional[str]
    transaction_id: Optional[str]
    original_transaction_id: Optional[str]
    currency: Optional[str]
    price: Optional[float]
    price_in_purchased_currency: Optional[float]
    store: str
    takehome_percentage: Optional[float]
    offer_code: Optional[str]
    subscriber_attributes: Optional[Dict[str, SubscriberAttribute]]
    purchased_at_ms: Optional[int]
    expiration_at_ms: Optional[int]
    is_family_share: Optional[bool]
    country_code: Optional[str]


# 각 이벤트는 BaseEvent에 없는 추가 필드만 정의
class InitialPurchase(BaseEvent):
    is_trial_conversion: Optional[bool]


class Cancellation(BaseEvent):
    cancel_reason: str


class Uncancellation(BaseEvent):
    pass


class Renewal(BaseEvent):
    is_trial_conversion: bool


class ProductChange(BaseEvent):
    new_product_id: str


class Test(BaseModel):
    # 기본 필드 (null이 아닌 필드들)
    event_timestamp_ms: int
    environment: str
    type: EventType
    id: str
    app_id: str
    app_user_id: str
    original_app_user_id: str
    aliases: List[str]
    period_type: str
    product_id: str
    store: str
    purchased_at_ms: int
    expiration_at_ms: int
    subscriber_attributes: Dict[str, SubscriberAttribute]

    # Optional 필드들 (null이 올 수 있는 필드들)
    commission_percentage: Optional[float]
    country_code: Optional[str]
    currency: Optional[str]
    entitlement_id: Optional[str]
    entitlement_ids: Optional[List[str]]
    is_family_share: Optional[bool]
    offer_code: Optional[str]
    original_transaction_id: Optional[str]
    presented_offering_id: Optional[str]
    price: Optional[float]
    price_in_purchased_currency: Optional[float]
    renewal_number: Optional[int]
    takehome_percentage: Optional[float]
    tax_percentage: Optional[float]
    transaction_id: Optional[str]

class WebhookEvent(BaseModel):
    api_version: str
    event: dict

    def parse_event(self) -> BaseEvent:
        event_type = EventType(self.event["type"])
        event_data = self.event

        event_models = {
            EventType.INITIAL_PURCHASE: InitialPurchase,
            EventType.CANCELLATION: Cancellation,
            EventType.UNCANCELLATION: Uncancellation,
            EventType.RENEWAL: Renewal,
            EventType.PRODUCT_CHANGE: ProductChange,
            EventType.TEST: Test,
        }

        event_class = event_models[event_type]
        return event_class.model_validate(event_data)

    @classmethod
    def from_payload(cls, payload: dict) -> 'WebhookEvent':
        return cls.model_validate(payload)

