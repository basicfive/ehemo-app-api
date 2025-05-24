from uuid import uuid4
from app.core.config import aws_s3_settings

def create_uploaded_image_for_training_s3_key() -> str:
    return aws_s3_settings.USER_UPLOADED_IMAGE_FOR_TRAINING_S3KEY_PREFIX + str(uuid4())