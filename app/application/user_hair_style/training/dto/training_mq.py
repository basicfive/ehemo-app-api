from pydantic import BaseModel
from typing import List
from app.domain.common.enums.gender import Gender


class TrainingPublishMessage(BaseModel):
    gender: Gender
    training_job_id: int
    user_hair_lora_s3_key: str
    user_hair_lora_name: str
    uploaded_image_s3_keys: List[str]
    total_steps: int
    epoch: int

class TrainingConsumeMessage(BaseModel):
    training_job_id: int
    is_success: bool
    user_hair_lora_s3_key: str
    user_hair_lora_name: str
    actual_training_time_sec: int

