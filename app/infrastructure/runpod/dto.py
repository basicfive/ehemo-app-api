from pydantic import BaseModel
from typing import Optional, List

class Output(BaseModel):
    upload_url: str
    image_format: str

class RunpodRequest(BaseModel):
    input: dict

class InferencePayload(BaseModel):
    webhook_url: str
    outputs: List[Output]

    job_id: int

    is_img2img: bool
    image_url: Optional[str]
    width: Optional[int]
    height: Optional[int]
    iterations: int
    is_upscale: bool

    prompt: str
    lora_name: str
    denoise: float

class WebhookResponse(BaseModel):
    job_id: int
    is_success: bool
