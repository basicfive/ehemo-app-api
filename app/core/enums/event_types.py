from typing import Optional
from enum import Enum

class EventType(str, Enum):
    THUMBNAIL_GENERATION = "thumbnail_generation"
    UPSCALE = "upscale"

    @classmethod
    def from_string(cls, value: str) -> Optional['EventType']:
        """문자열을 EventType으로 변환"""
        try:
            return cls(value)
        except ValueError:
            return None
