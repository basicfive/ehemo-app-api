from enum import Enum

class TokenTransactionType(Enum):
    REFILL = "REFILL"
    REFUND = "REFUND"
    USE = "USE"
    EXPIRE= "EXPIRE"
    MANUAL_ADJUST = "MANUAL_ADJUST"

class TokenSourceType(Enum):
    SUBSCRIPTION_RENEWAL = "SUBSCRIPTION_RENEWAL"
    INITIAL = "INITIAL"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    ADMIN = "ADMIN"

