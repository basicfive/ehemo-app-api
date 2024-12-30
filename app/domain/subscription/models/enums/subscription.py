from enum import Enum

class StoreType(str, Enum):
    APP_STORE = "APP_STORE"
    PLAY_STORE = "PLAY_STORE"

class SubscriptionPlanType(Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"

class BillingInterval(Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class SubscriptionStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"
    PENDING = "PENDING"
    CHANGED = "CHANGED"
    TRIAL = "TRIAL"

class Currency(str, Enum):
    USD = "USD"
    KRW = "KRW"
    JPY = "JPY"
    EUR = "EUR"