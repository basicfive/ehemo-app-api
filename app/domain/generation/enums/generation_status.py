from enum import Enum

class GenerationJobStatus(Enum):
    PENDING = "PENDING"
    PENDING_UPSCALE = "PENDING_UPSCALE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class GenerationRequestResult(Enum):
    PENDING = "PENDING"
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

