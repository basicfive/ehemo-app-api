from enum import Enum

class GeneratedImageStatus(str, Enum):
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    UPSCALED = "UPSCALED"
    FAILED = "FAILED"
    DELETED = "DELETED"
    REPORTED = "REPORTED"