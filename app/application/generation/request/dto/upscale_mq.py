from pydantic import BaseModel
from typing import List

from app.core.enums.inference_types import InferenceType

class UpscaleImageInfo(BaseModel):
    generated_image_id: int
    s3_key: str
    upscale_s3_key: str

class UpscalePublishMessage(BaseModel):
    image_info_list: List[UpscaleImageInfo]
    time_to_live_sec: int

    prompt: str
    width: int
    height: int

class UpscaleConsumeMessage(BaseModel):
    is_success: bool

class NormalUpscalePublishMessage(UpscalePublishMessage):
    inference_type: InferenceType = InferenceType.NORMAL
    generation_job_id: int

class NormalUpscaleConsumeMessage(UpscaleConsumeMessage):
    inference_type: InferenceType = InferenceType.NORMAL
    generation_job_id: int