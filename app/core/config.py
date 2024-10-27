from pydantic import BaseModel
import os

from dotenv import load_dotenv

load_dotenv()

class Setting(BaseModel):
    PROJECT_NAME: str = "ehemo-app-api"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST'),
    RABBITMQ_VHOST: str = os.getenv('RABBITMQ_VHOST'),
    RABBITMQ_USERNAME: str = os.getenv('RABBITMQ_USERNAME'),
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_PASSWORD'),
    RABBITMQ_PUBLISH_QUEUE: str = os.getenv('RABBITMQ_PUBLISH_QUEUE'),
    RABBITMQ_CONSUME_QUEUE: str = os.getenv('RABBITMQ_CONSUME_QUEUE')

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")


settings = Setting()