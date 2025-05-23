from enum import Enum
from dataclasses import dataclass
from typing import Any


@dataclass
class SimilarityValue:
    code: str  # DB에 저장될 값
    float_value: float

    def __str__(self) -> str:
        return self.code


class ReferenceImageSimilarity(Enum):
    LOW = SimilarityValue("LOW", 1.0)
    MEDIUM = SimilarityValue("MEDIUM", 0.9)
    HIGH = SimilarityValue("HIGH", 0.7)
    
    @classmethod
    def _missing_(cls, value):
        """Pydantic이 문자열을 enum으로 변환할 수 있도록 지원"""
        if isinstance(value, str):
            for member in cls:
                if member.value.code == value:
                    return member
        return None
    
    @property
    def float_value(self) -> float:
        return self.value.float_value
    
    def __str__(self) -> str:
        return self.value.code