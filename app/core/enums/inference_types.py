from typing import Optional
from enum import Enum

class InferenceType(str, Enum):
    NORMAL = "normal"
    THUMBNAIL = "thumbnail"

    @classmethod
    def from_string(cls, value: str) -> Optional['InferenceType']:
        """문자열을 InferenceType으로 변환"""
        try:
            return cls(value)
        except ValueError:
            return None
