from uuid import uuid4

from app.core.config import aws_s3_settings

def create_reference_image_s3_key() -> str:
    return aws_s3_settings.USER_REFERENCE_IMAGE_S3KEY_PREFIX + str(uuid4())
