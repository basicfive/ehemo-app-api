from pydantic import BaseModel
import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class BaseSetting(BaseModel):
    PROJECT_NAME: str = "ehemo-app-api"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL")

class RabbitMQSetting(BaseSetting):
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST')
    RABBITMQ_VHOST: str = os.getenv('RABBITMQ_VHOST')
    RABBITMQ_USERNAME: str = os.getenv('RABBITMQ_USERNAME')
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_PUBLISH_QUEUE: str = os.getenv('RABBITMQ_PUBLISH_QUEUE')
    RABBITMQ_CONSUME_QUEUE: str = os.getenv('RABBITMQ_CONSUME_QUEUE')

class RedisSetting(BaseSetting):
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")

class AWSS3Setting(BaseSetting):
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    REGION_NAME: str = os.getenv("REGION_NAME")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME")

    GENERATED_IMAGE_S3KEY_PREFIX: str = "generated_image/"
    GENERATED_IMAGE_GROUP_S3KEY_PREFIX: str = "generated_image_group_thumbnail/"

class JwtSetting(BaseModel):
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

class OAuthSetting(BaseModel):
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID")
    KAKAO_CLIENT_ID: str = os.getenv("KAKAO_CLIENT_ID")

    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")
    APPLE_REDIRECT_URI: str = os.getenv("APPLE_REDIRECT_URI")
    KAKAO_REDIRECT_URI: str = os.getenv("KAKAO_REDIRECT_URI")

class ImageGenerationSetting(BaseModel):
    SINGLE_INFERENCE_IMAGE_CNT: int = 2
    DISTILLED_CFG_SCALE: float = 2.0
    SINGLE_IMAGE_INFERENCE_SEC: int = 30


base_settings = BaseSetting()
rabbit_mq_setting = RabbitMQSetting()
redis_setting = RedisSetting()
aws_s3_setting = AWSS3Setting()
jwt_setting = JwtSetting()
oauth_setting = OAuthSetting()
image_generation_setting = ImageGenerationSetting()
