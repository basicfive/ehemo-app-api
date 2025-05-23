from typing import Tuple
from uuid import uuid4

from app.domain.common.enums.gender import Gender
from app.core.config import aws_s3_settings

# TODO: 썸네일 생성 용 기본 프롬프트 설정 필요
def create_thumbnail_prompt(gender: Gender) -> str:
    if gender == Gender.MALE:
        return "male"
    else:
        return "female"

def get_thumbnail_image_size() -> Tuple[int, int]:
    width = 896
    height = 1152
    return width, height

def create_user_hair_style_thumbnail_s3_key() -> str:
    return aws_s3_settings.USER_HAIR_STYLE_THUMBNAIL_S3KEY_PREFIX + str(uuid4())

