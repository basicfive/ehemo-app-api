from enum import IntEnum

class MessagePriority(IntEnum):
    LOW = 0
    NORMAL = 3
    HIGH = 7
    URGENT = 10