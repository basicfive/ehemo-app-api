from typing import Optional
from pydantic import BaseModel

from app.core.enums.generation_status import GenerationStatusEnum


class ImageGenerationJobCreate(BaseModel):
    prompt: str
    distilled_cfg_scale: float
    width: int
    height: int
    generation_request_id: int

class ImageGenerationJobUpdate(BaseModel):
    prompt: Optional[str]
    distilled_cfg_scale: Optional[float]
    status: Optional[GenerationStatusEnum]
    s3_key: Optional[str]
    webui_png_info: Optional[str]
    width: Optional[int]
    height: Optional[int]
    generation_request_id: Optional[int]

class ImageGenerationJobInDB(BaseModel):
    id: int
    prompt: str
    status: GenerationStatusEnum
    s3_key: Optional[str]
    webui_png_info: Optional[str]
    distilled_cfg_scale: float
    width: int
    height: int
    generation_request_id: int

    class Config:
        from_attributes=True