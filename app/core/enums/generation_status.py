from enum import Enum

class GenerationStatusEnum(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationResultEnum(Enum):
    PENDING = "pending"
    SUCCEED = "succeed"
    FAILED = "failed"
    CANCELED = "canceled"

