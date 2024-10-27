from pydantic import BaseModel

class GeneratedImageData(BaseModel):
    id: int
    user_id: int
    image_url: str
    generated_image_group_id: int

class GeneratedImageGroupData(BaseModel):
    id: int
    user_id: int
    generation_request_id: int
    thumbnail_image_url: str
