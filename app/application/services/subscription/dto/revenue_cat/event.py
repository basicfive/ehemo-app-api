from enum import Enum
from typing import List, Optional, Dict, Type
from pydantic import BaseModel

from app.domain import StoreType, Currency


class EventType(str, Enum):
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    CANCELLATION = "CANCELLATION"
    UNCANCELLATION = "UNCANCELLATION"
    RENEWAL = "RENEWAL"
    PRODUCT_CHANGE = "PRODUCT_CHANGE"
    EXPIRATION = "EXPIRATION"
    TEST = "TEST"

class SubscriberAttribute(BaseModel):
    updated_at_ms: int
    value: str


class BaseEvent(BaseModel):
    type: EventType
    id: str
    app_id: str
    event_timestamp_ms: int
    app_user_id: str
    original_app_user_id: str
    aliases: List[str]
    subscriber_attributes: Optional[Dict[str, SubscriberAttribute]]

    product_id: str
    entitlement_ids: Optional[List[str]]
    period_type: str
    purchased_at_ms: int

    # It can be NULL for non-subscription purchases.
    expiration_at_ms: Optional[int]

    store: StoreType
    environment: str

    presented_offering_id: Optional[str]
    price: Optional[float]
    currency: Optional[Currency]
    price_in_purchased_currency: Optional[float]
    tax_percentage: Optional[float]  # 추가
    commission_percentage: Optional[float]  # 추가

    transaction_id: str
    original_transaction_id: str
    country_code: str


class InitialPurchase(BaseEvent):
    pass


class Cancellation(BaseEvent):
    cancel_reason: str


class Uncancellation(BaseEvent):
    pass


class Renewal(BaseEvent):
    is_trial_conversion: bool


class ProductChange(BaseEvent):
    new_product_id: str


class Expiration(BaseEvent):
    expiration_reason: str


class EventParser:
    _parsers: Dict[EventType, Type[BaseEvent]] = {
        EventType.INITIAL_PURCHASE: InitialPurchase,
        EventType.CANCELLATION: Cancellation,
        EventType.UNCANCELLATION: Uncancellation,
        EventType.RENEWAL: Renewal,
        EventType.PRODUCT_CHANGE: ProductChange,
        EventType.EXPIRATION: Expiration,
        # EventType.TEST: Test
    }

    @classmethod
    def parse(cls, event_data: dict) -> BaseEvent:
        # 1. subscriber_attributes 전처리
        if "subscriber_attributes" in event_data and event_data["subscriber_attributes"]:
            event_data["subscriber_attributes"] = {
                key: SubscriberAttribute.model_validate(value)
                for key, value in event_data["subscriber_attributes"].items()
            }

        # 2. event_type 가져오기 (Enum은 자동변환됨)
        event_type = EventType(event_data["type"])
        parser = cls._parsers.get(event_type)

        if not parser:
            raise ValueError(f"Unsupported event type: {event_type}")

        # 3. 해당 이벤트 타입의 모델로 변환
        return parser.model_validate(event_data)


