from typing import Optional
from pydantic import BaseModel

class ImageGenerationJobCreate(BaseModel):
    prompt: str
    distilled_cfg_scale: float
    width: int
    height: int
    generation_request_id: int

class ImageGenerationJobUpdate(BaseModel):
    prompt: Optional[str]
    distilled_cfg_scale: Optional[float]
    width: Optional[int]
    height: Optional[int]
    generation_request_id: Optional[int]

class ImageGenerationJobInDB(BaseModel):
    prompt: str
    distilled_cfg_scale: float
    width: int
    height: int
    generation_request_id: int

    class Config:
        from_attributes=True