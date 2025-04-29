from enum import Enum

class TrainingRequestStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class TrainingJobStatus(str, Enum):
    PENDING = "PENDING"
    # mq 서버에서 현재 학습 중인지 값을 보내주지 않는 한 알기 어려움
    TRAINING = "TRAINING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GenerationRequestStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class GenerationJobStatus(str, Enum):
    PENDING = "PENDING"
    # mq 서버에서 현재 추론 중인지 값을 보내주지 않는 한 알기 어려움
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
