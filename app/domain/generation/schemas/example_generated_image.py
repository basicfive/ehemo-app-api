from typing import Optional
from pydantic import BaseModel

class ExampleGeneratedImageCreate(BaseModel):
    s3_key: str
    generated_image_group_id: int

class ExampleGeneratedImageUpdate(BaseModel):
    s3_key: Optional[str] = None
    webui_png_info: Optional[str] = None
    deleted: Optional[bool] = None
    generated_image_group_id: Optional[int] = None

class ExampleGeneratedImageInDB(BaseModel):
    s3_key: str
    webui_png_info: Optional[str]
    deleted: bool
    generated_image_group_id: int

    class Config:
        from_attributes=True
