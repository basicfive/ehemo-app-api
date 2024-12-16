from enum import Enum

class StoreType(Enum):
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
    TRIAL = "TRIAL"
