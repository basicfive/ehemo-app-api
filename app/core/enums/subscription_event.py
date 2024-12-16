from enum import Enum
from typing import Literal

class RevenueCatEventType(Enum):
    INITIAL_PURCHASE = "INITIAL_PURCHASE"
    RENEWAL = "RENEWAL"
    EXPIRATION = "EXPIRATION"
    CANCELLATION = "CANCELLATION"

    @classmethod
    def from_str(cls, value: str) -> "RevenueCatEventType":
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Unknown RevenueCat event type: {value}")