from datetime import datetime
from typing import List, Optional, Any, Dict
from enum import Enum
from pydantic import BaseModel


class ReplicateStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"

class ReplicateMetrics(BaseModel):
    predict_time: float

class ReplicateUrls(BaseModel):
    cancel: str
    get: str
    web: str

class ReplicateResponse(BaseModel):
    completed_at: Optional[datetime] = None
    created_at: datetime
    data_removed: bool
    deployment: str
    error: Optional[Any] = None
    id: str
    input: Dict[str, Any]
    logs: str
    metrics: ReplicateMetrics
    model: str
    output: Dict[str, Any]
    started_at: datetime
    status: ReplicateStatus
    urls: ReplicateUrls
    version: str
    webhook: Optional[str] = None
    webhook_events_filter: Optional[List[str]] = None
