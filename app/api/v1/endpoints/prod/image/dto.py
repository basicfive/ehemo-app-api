from pydantic import BaseModel
from typing import List
from app.domain.generation.schemas.generated_image import GeneratedImageInDB

class ImageByGroupRequest(BaseModel):
    generated_image_group_id: int

# class ImageFromGroupResponse(BaseModel):
#     image_list: List[GeneratedImageInDB]

class ImageGroupByUserRequest(BaseModel):
    user_id: int
