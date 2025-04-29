from uuid import uuid4

from app.core.config import aws_s3_settings

def create_user_hair_lora_name() -> str:
    return str(uuid4())

def create_user_hair_lora_s3_key(user_hair_lora_name: str) -> str:
    return aws_s3_settings.USER_HAIR_STYLE_LORA_S3KEY_PREFIX + user_hair_lora_name

def create_user_hair_style_thumbnail_s3_key() -> str:
    return aws_s3_settings.USER_HAIR_STYLE_THUMBNAIL_S3KEY_PREFIX + str(uuid4())



