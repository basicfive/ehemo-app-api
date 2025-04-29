from pydantic import BaseModel
from typing import List

from app.application.generation.request.dto.generation_mq import ImageInfo

class UpscalePublishMessage(BaseModel):
    generation_job_id: int
    image_info_list: List[ImageInfo]
    time_to_live_sec: int

class UpscaleConsumeMessage(BaseModel):
    is_success: bool
    generation_job_id: int
