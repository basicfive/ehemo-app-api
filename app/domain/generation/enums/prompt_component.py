from enum import Enum

class PromptComponentType(str, Enum):
    HAIR_LENGTH = "HAIR_LENGTH"
    HAIR_COLOR = "HAIR_COLOR"
    BACKGROUND = "BACKGROUND"
    POSE = "POSE"
    CLOTHING = "CLOTHING"
    ADDITIONAL_REQUEST = "ADDITIONAL_REQUEST"
