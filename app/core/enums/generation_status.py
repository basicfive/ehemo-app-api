from enum import Enum

class GenerationStatusEnum(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class NotificationStatus(Enum):
    PENDING = "pending"
    SUCCESS_NOTIFIED = "success_notified"
    FAILURE_NOTIFIED = "failure_notified"