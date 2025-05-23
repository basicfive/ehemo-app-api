from enum import Enum

class UserHairStyleStatus(str, Enum):
    PENDING = "PENDING"
    REGISTERED = "REGISTERED"
    FAILED = "FAILED"
    DELETED = "DELETED"