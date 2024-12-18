from enum import Enum

class GenerationStatusEnum(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class GenerationResultEnum(Enum):
    PENDING = "PENDING"
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

