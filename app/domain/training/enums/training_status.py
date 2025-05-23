from enum import Enum

class TrainingRequestStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class TrainingJobStatus(str, Enum):
    PENDING = "PENDING"
    THUMBNAIL_GENERATING = "THUMBNAIL_GENERATING"
    THUMBNAIL_UPSCALING = "THUMBNAIL_UPSCALING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
