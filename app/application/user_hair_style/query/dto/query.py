from pydantic import BaseModel
from datetime import datetime
from typing import List

from app.domain.common.enums.gender import Gender
from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus

class UploadedImageData(BaseModel):
    s3_key: str
    url: str

class UserHairStyleInfo(BaseModel):
    id: int
    gender: Gender
    status: UserHairStyleStatus
    created_at: datetime
    thumbnail_url: str
    title: str
    description: str

class UserHairStyleDetail(BaseModel):
    id: int
    uploaded_image_data_list: List[UploadedImageData]
