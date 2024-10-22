from pydantic import BaseModel

class MQConsumeMessage(BaseModel):
    image_generation_job_id: int
    webui_png_info: str
    s3_key: str

class MQPublishMessage(BaseModel):
    generation_request_id: int
    prompt: str
    distilled_cfg_scale: float
    width: int
    height: int
    image_generation_job_id: int
    s3_key: str
