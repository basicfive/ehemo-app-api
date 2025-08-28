from typing import Optional
from pydantic import BaseModel

from app.infrastructure.fcm.notification_type import NotificationType

class FCMData(BaseModel):
    type: NotificationType
    id: Optional[str] = None