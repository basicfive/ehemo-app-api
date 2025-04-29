from typing import Tuple

from app.domain.common.enums.gender import Gender

def create_thumbnail_prompt(gender: Gender) -> str:
    if gender == Gender.MALE:
        return "male"
    else:
        return "female"

def get_thumbnail_image_size() -> Tuple[int, int]:
    return 896, 1152