from enum import Enum
from typing import List, Optional, Dict, Type, Union
from pydantic import BaseModel, ConfigDict

from app.domain import StoreType, Currency


class EventType(str, Enum):
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    CANCELLATION = "CANCELLATION"
    UNCANCELLATION = "UNCANCELLATION"
    RENEWAL = "RENEWAL"
    PRODUCT_CHANGE = "PRODUCT_CHANGE"
    EXPIRATION = "EXPIRATION"
    TRANSFER = "TRANSFER"
    TEST = "TEST"

class SubscriberAttribute(BaseModel):
    updated_at_ms: int
    value: str

class BaseEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    event_timestamp_ms: int
    product_id: str
    period_type: str
    purchased_at_ms: int

    # It can be NULL for non-subscription purchases.
    expiration_at_ms: Optional[int]

    environment: str
    entitlement_ids: Optional[List[str]]
    presented_offering_id: Optional[str]
    transaction_id: str
    original_transaction_id: str
    country_code: str
    app_user_id: str
    aliases: List[str]
    original_app_user_id: str
    currency: Optional[Currency]
    price: Optional[float]
    price_in_purchased_currency: Optional[float]
    subscriber_attributes: Optional[Dict[str, SubscriberAttribute]]
    store: StoreType
    tax_percentage: Optional[float]  # 추가
    commission_percentage: Optional[float]  # 추가

    type: EventType
    id: str
    app_id: str


class InitialPurchase(BaseEvent):
    model_config = ConfigDict(extra='ignore')
    pass


class Cancellation(BaseEvent):
    model_config = ConfigDict(extra='ignore')
    cancel_reason: str


class Uncancellation(BaseEvent):
    model_config = ConfigDict(extra='ignore')
    pass


class Renewal(BaseEvent):
    model_config = ConfigDict(extra='ignore')
    is_trial_conversion: bool


class ProductChange(BaseEvent):
    model_config = ConfigDict(extra='ignore')
    new_product_id: str


class Expiration(BaseEvent):
    model_config = ConfigDict(extra='ignore')
    expiration_reason: str


class Transfer(BaseModel):
    model_config = ConfigDict(extra='ignore')
    event_timestamp_ms: int
    subscriber_attributes: Optional[Dict[str, SubscriberAttribute]]

    store: StoreType
    transferred_from: List[str]
    transferred_to: List[str]
    environment: str
    type: EventType
    id: str
    app_id: str


class EventParser:
    _parsers: Dict[EventType, Type[Union[BaseEvent, Transfer]]] = {
        EventType.INITIAL_PURCHASE: InitialPurchase,
        EventType.CANCELLATION: Cancellation,
        EventType.UNCANCELLATION: Uncancellation,
        EventType.RENEWAL: Renewal,
        EventType.PRODUCT_CHANGE: ProductChange,
        EventType.EXPIRATION: Expiration,
        EventType.TRANSFER: Transfer,
        # EventType.TEST: Test
    }

    @classmethod
    def parse(cls, event_data: dict) -> Union[BaseEvent, Transfer]:
        # 1. subscriber_attributes 전처리는 모든 이벤트에 공통으로 적용
        if "subscriber_attributes" in event_data and event_data["subscriber_attributes"]:
            event_data["subscriber_attributes"] = {
                key: SubscriberAttribute.model_validate(value)
                for key, value in event_data["subscriber_attributes"].items()
            }

        # 2. event_type 확인
        event_type = EventType(event_data["type"])
        print("event_type")
        print(event_type)
        parser = cls._parsers.get(event_type)
        print("parser")
        print(parser)

        print("event_data")
        print(event_data)

        if not parser:
            raise ValueError(f"Unsupported event type: {event_type}")

        # 3. 해당 이벤트 타입의 모델로 변환
        return parser.model_validate(event_data)