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
    
    @property
    def float_value(self) -> float:
        return self.value.float_value
    
    def __str__(self) -> str:
        return self.value.code