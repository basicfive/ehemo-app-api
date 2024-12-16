from pydantic import BaseModel
import os

from dotenv import load_dotenv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

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

    PRESIGNED_URL_EXPIRATION_SEC: int = 3600;

class JwtSetting(BaseModel):
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

class OAuthSetting(BaseModel):
    # google web
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000" + os.getenv("GOOGLE_REDIRECT_ENDPOINT")

    # google mobile (firebase)
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY")
    FIREBASE_CREDENTIALS_PATH: str = os.path.join(ROOT_DIR, "firebase-adminsdk.json")

    # apple mobile
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID")
    APPLE_REDIRECT_URI: str = "https://" + os.getenv("SERVICE_DOMAIN") + os.getenv("APPLE_REDIRECT_ENDPOINT")
    APPLE_PRIVATE_KEY: str = os.getenv("APPLE_PRIVATE_KEY")
    APPLE_TEAM_ID: str = os.getenv("APPLE_TEAM_ID")
    APPLE_KEY_ID: str = os.getenv("APPLE_KEY_ID")

    # kakao mobile
    KAKAO_CLIENT_ID: str = os.getenv("KAKAO_CLIENT_ID")
    KAKAO_CLIENT_SECRET: str = os.getenv("KAKAO_CLIENT_SECRET")

class ImageGenerationSetting(BaseModel):
    GENERATED_IMAGE_CNT_PER_REQUEST: int = 10
    DISTILLED_CFG_SCALE: float = 2.0
    # 이걸 고정 상수로 두는게 맞나..?
    SINGLE_INFERENCE_SEC_EST: int = 60

    WAIT_TIME_BUFFER_MULT: float = 1.2
    RETRY_WAIT_TIME_BUFFER_MULT: float = 1.0

    MESSAGE_TTL_MULTIPLIER: float = 1.0
    RETRY_MESSAGE_TTL_MULTIPLIER: float = 2.0
    MAX_RETRIES: int = 1

class TokenSetting(BaseModel):
    MONTHLY_REFILLED_TOKEN: int = 15
    FREE_TRIAL_TOKEN: int = 1

class FCMSetting(BaseModel):
    SUCCESS_TITLE: str = "AI 모델 이미지 생성이 완료되었어요"
    SUCCESS_BODY: str = "생성된 이미지를 확인해보세요"

    CATEGORY: str = "GENERATION_RESULT"
    IDENTIFIER_PREFIX: str = "request_"

    FAILURE_TITLE: str = "AI 모델 이미지 생성에 실패했어요"
    FAILURE_BODY: str = "토큰은 반환되었으니, 잠시 후에 다시 시도해주세요"

    TOKEN_REFILL_TITLE: str = "토큰이 리필되었어요"
    TOKEN_REFILL_BODY: str = "토큰이 리필되었어요"

class RevenueCatSetting(BaseModel):
    AUTHORIZATION_HEADER_UUID: str = os.getenv("REVENUECAT_UUID")


class TimezoneConfig(BaseModel):
    SEOUL: str = "Asia/Seoul"
    UTC: str = "UTC"


base_settings = BaseSetting()
rabbit_mq_setting = RabbitMQSetting()
redis_setting = RedisSetting()
aws_s3_setting = AWSS3Setting()
jwt_setting = JwtSetting()
oauth_setting = OAuthSetting()
image_generation_setting = ImageGenerationSetting()
token_setting = TokenSetting()
fcm_setting = FCMSetting()
timezone_config = TimezoneConfig()