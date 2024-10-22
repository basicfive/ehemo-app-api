from typing import Optional
from pydantic import BaseModel

class GeneratedImageCreate(BaseModel):
    user_id: int
    s3_key: str
    webui_png_info: str
    generation_request_id: int
    generated_image_group_id: int
    image_generation_job_id: int

class GeneratedImageUpdate(BaseModel):
    user_id: Optional[int]
    s3_key: Optional[int]
    webui_png_info: Optional[int]
    generation_request_id: Optional[int]
    generated_image_group_id: Optional[int]
    image_generation_job_id: Optional[int]

class GeneratedImageInDB(BaseModel):
    id: int
    user_id: int
    s3_key: str
    webui_png_info: str
    generation_request_id: int
    generated_image_group_id: int
    image_generation_job_id: int

    class Config:
        from_attributes=True
