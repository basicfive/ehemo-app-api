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
    ALERT_DISCORD_WEBHOOK: str = os.getenv("ALERT_DISCORD_WEBHOOK")

class RabbitMQSetting(BaseSetting):
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST')
    RABBITMQ_VHOST: str = os.getenv('RABBITMQ_VHOST')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT'))
    RABBITMQ_USERNAME: str = os.getenv('RABBITMQ_USERNAME')
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_PASSWORD')

    RABBITMQ_INFERENCE_PUBLISH: str = os.getenv('RABBITMQ_INFERENCE_PUBLISH')
    RABBITMQ_INFERENCE_CONSUME: str = os.getenv('RABBITMQ_INFERENCE_CONSUME')

    RABBITMQ_UPSCALE_PUBLISH: str = os.getenv('RABBITMQ_UPSCALE_PUBLISH')
    RABBITMQ_UPSCALE_CONSUME: str = os.getenv('RABBITMQ_UPSCALE_CONSUME')

    RABBITMQ_TRAINING_PUBLISH: str = os.getenv('RABBITMQ_TRAINING_PUBLISH')
    RABBITMQ_TRAINING_CONSUME: str = os.getenv('RABBITMQ_TRAINING_CONSUME')


class RedisSetting(BaseSetting):
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: str = os.getenv("REDIS_PORT")

class AWSS3Setting(BaseSetting):
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    REGION_NAME: str = os.getenv("REGION_NAME")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME")

    GENERATED_IMAGE_S3KEY_PREFIX: str = "generated_image/"

    USER_REFERENCE_IMAGE_S3KEY_PREFIX: str = "user_reference_image/"

    USER_UPLOADED_IMAGE_FOR_TRAINING_S3KEY_PREFIX: str = "user_uploaded_image_for_training/"
    USER_HAIR_STYLE_LORA_S3KEY_PREFIX: str = "user_hair_style_lora/"
    USER_HAIR_STYLE_THUMBNAIL_S3KEY_PREFIX: str = "user_hair_style_thumbnail/"

    PRESIGNED_URL_EXPIRATION_SEC: int = 3600

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
    GENERATED_IMAGE_CNT_PER_REQUEST: int = 4
    DISTILLED_CFG_SCALE: float = 2.0

    # SINGLE_INFERENCE_SEC_EST: int = 1000
    SINGLE_INFERENCE_SEC_EST: int = 30
    SINGLE_INFERENCE_HIGH_RES_SEC_EST: int = 60
    
    SINGLE_INFERENCE_UPSCALE_SEC_EST: int = 180
    # SINGLE_INFERENCE_UPSCALE_SEC_EST: int = 10

    IMAGE_GENERATION_JOB_EXPIRE_TIME_MULTIPLIER: float = 1.2

class TokenSetting(BaseModel):
    MONTHLY_REFILLED_TOKEN: int = 1500
    FREE_TRIAL_TOKEN: int = 100

    BASE_TOKENS_PER_GENERATION: int = 100

class RevenueCatSetting(BaseModel):
    AUTHORIZATION_HEADER_UUID: str = os.getenv("REVENUECAT_UUID")

class TimezoneSetting(BaseModel):
    SEOUL: str = "Asia/Seoul"
    UTC: str = "UTC"

class TrainingSetting(BaseModel):
    MINIMUM_IMAGE_CNT_FOR_TRAINING: int = 30
    MAXIMUM_IMAGE_CNT_FOR_TRAINING: int = 100

    MINIMUM_IMAGE_CNT_FOR_QUALITY_GUARANTEE: int = 70

    TIME_PER_STEP_ON_A100_SEC: float = 3.34
    MINIMUM_TRAINING_STEPS: int = 14000
    MINIMUM_EPOCH: int = 200
    MINIMUM_ESTIAMATE_TRAINING_TIME_SEC: int = 46800  # 13 hours

    TRAINING_JOB_EXPIRE_TIME_MULTIPLIER: float = 1.1

class VersioningSetting(BaseModel):
    APP_VERSION_IOS_STORE_URL: str = os.getenv("APP_VERSION_IOS_STORE_URL")
    APP_VERSION_ANDROID_STORE_URL: str = os.getenv("APP_VERSION_ANDROID_STORE_URL")

base_settings = BaseSetting()
rabbit_mq_settings = RabbitMQSetting()
redis_settings = RedisSetting()
aws_s3_settings = AWSS3Setting()
jwt_settings = JwtSetting()
oauth_settings = OAuthSetting()
image_generation_settings = ImageGenerationSetting()
token_settings = TokenSetting()
revenuecat_settings = RevenueCatSetting()
timezone_settings = TimezoneSetting()
training_settings = TrainingSetting()
versioning_settings = VersioningSetting()