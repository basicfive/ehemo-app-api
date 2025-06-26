from pydantic import BaseModel
from typing import List

class UpscaleImageInfo(BaseModel):
    generated_image_id: int
    s3_key: str
    upscale_s3_key: str

class UpscalePublishMessage(BaseModel):
    generation_job_id: int
    image_info_list: List[UpscaleImageInfo]
    time_to_live_sec: int

    prompt: str
    width: int
    height: int

class UpscaleConsumeMessage(BaseModel):
    generation_job_id: int
    is_success: bool
