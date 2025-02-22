from typing import Optional
from pydantic import BaseModel

class MQConsumeMessage(BaseModel):
    image_generation_job_id: int
    webui_png_info: str
    s3_key: str

    def to_str(self) -> str:
        return self.model_dump_json()

class MQPublishMessage(BaseModel):
    generation_request_id: int
    image_generation_job_id: int
    s3_key: str
    matting_bgr_key: Optional[str] = None

    prompt: str
    lora_model: str
    is_upscale: bool
    is_custom_bgr: bool
    distilled_cfg_scale: float
    width: int
    height: int

    def to_str(self) -> str:
        return self.model_dump_json()

    def to_json(self) -> bytes:
        return self.model_dump_json().encode('utf-8')
