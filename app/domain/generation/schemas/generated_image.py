from typing import Optional
from pydantic import BaseModel

class GeneratedImageCreate(BaseModel):
    user_id: int
    s3_key: str
    webui_png_info: str
    is_custom_background: bool
    generated_image_group_id: int
    image_generation_job_id: int

class GeneratedImageUpdate(BaseModel):
    user_id: Optional[int] = None
    s3_key: Optional[str] = None
    last_modified_image_key: Optional[str] = None
    webui_png_info: Optional[str] = None
    is_custom_background: Optional[bool] = None
    generated_image_group_id: Optional[int] = None
    image_generation_job_id: Optional[int] = None

class GeneratedImageInDB(BaseModel):
    id: int
    user_id: int
    s3_key: str
    last_modified_image_key: Optional[str]
    webui_png_info: str
    is_custom_background: bool
    generated_image_group_id: int
    image_generation_job_id: int

    class Config:
        from_attributes=True
