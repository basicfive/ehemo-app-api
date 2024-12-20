from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel

class EventType(str, Enum):
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    CANCELLATION = "CANCELLATION"
    UNCANCELLATION = "UNCANCELLATION"
    RENEWAL = "RENEWAL"
    PRODUCT_CHANGE = "PRODUCT_CHANGE"

class SubscriberAttribute(BaseModel):
    updated_at_ms: int
    value: str

class BaseEvent(BaseModel):
    # 기본 이벤트 정보
    event_timestamp_ms: int
    environment: str
    type: EventType
    id: str
    app_id: str

    # 사용자 정보
    app_user_id: str
    original_app_user_id: str
    aliases: List[str]

    # 상품 정보
    product_id: str
    entitlement_id: Optional[str]
    entitlement_ids: List[str]
    presented_offering_id: Optional[str]

    # 결제 정보
    transaction_id: str
    original_transaction_id: str
    currency: str
    price: float
    price_in_purchased_currency: float
    store: str
    takehome_percentage: float

    # 기타 공통 필드
    period_type: str
    offer_code: Optional[str]
    subscriber_attributes: Dict[str, SubscriberAttribute]
    purchased_at_ms: int
    expiration_at_ms: int
    is_family_share: Optional[bool]
    country_code: Optional[str]


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
            EventType.PRODUCT_CHANGE: ProductChange
        }

        event_class = event_models[event_type]
        return event_class.model_validate(event_data)

    @classmethod
    def from_payload(cls, payload: dict) -> 'WebhookEvent':
        return cls.model_validate(payload)