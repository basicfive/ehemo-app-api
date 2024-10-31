from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.enums.generation_status import GenerationStatusEnum


class ImageGenerationJobCreate(BaseModel):
    expires_at: datetime
    retry_count: int

    s3_key: str
    prompt: str
    distilled_cfg_scale: float
    width: int
    height: int
    generation_request_id: int

class ImageGenerationJobUpdate(BaseModel):
    status: Optional[GenerationStatusEnum] = None
    expires_at: datetime = None
    retry_count: int = None

    s3_key: Optional[str] = None
    webui_png_info: Optional[str] = None
    prompt: Optional[str] = None
    distilled_cfg_scale: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    generation_request_id: Optional[int] = None

class ImageGenerationJobInDB(BaseModel):
    id: int
    status: GenerationStatusEnum
    expires_at: datetime
    retry_count: int

    s3_key: str
    webui_png_info: Optional[str]
    prompt: str
    distilled_cfg_scale: float
    width: int
    height: int
    generation_request_id: int

    class Config:
        from_attributes=True