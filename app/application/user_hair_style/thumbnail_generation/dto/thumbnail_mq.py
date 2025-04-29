from pydantic import BaseModel

from app.infrastructure.mq.dto.base_messages import InferenceBaseMessage

class ThumbnailGenerationPublishMessage(InferenceBaseMessage):
    training_request_id: int
    user_hair_lora_s3_key: str
    user_hair_lora_name: str
    thumbnail_s3_key: str

    prompt: str
    width: int
    height: int
    distilled_cfg_scale: float

class ThumbnailGenerationConsumeMessage(InferenceBaseMessage):
    training_request_id: int
    thumbnail_s3_key: str


