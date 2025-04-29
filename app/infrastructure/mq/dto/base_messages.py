from pydantic import BaseModel

from app.core.enums.event_types import EventType
from app.core.enums.inference_types import InferenceType

# class EventBusBaseMessage(BaseModel):
#     event_type: EventType

class InferenceBaseMessage(BaseModel):
    inference_type: InferenceType
