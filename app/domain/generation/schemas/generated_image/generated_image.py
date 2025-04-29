from typing import Optional
from pydantic import BaseModel

from app.domain.generation.enums.generated_image_status import GeneratedImageStatus

class GeneratedImageCreate(BaseModel):
    user_id: int
    s3_key: str
    upscaled_s3_key: str
    generation_job_id: int

class GeneratedImageUpdate(BaseModel):
    status: Optional[GeneratedImageStatus] = None
    upscaled_s3_key: Optional[str] = None
    webui_png_info: Optional[str] = None

class GeneratedImageInDB(BaseModel):
    id: int
    status: GeneratedImageStatus
    user_id: int
    s3_key: str
    upscaled_s3_key: str
    webui_png_info: Optional[str] = None
    generation_job_id: int

    class Config:
        from_attributes=True

