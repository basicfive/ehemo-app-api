from typing import Optional
from pydantic import BaseModel

class HairStyleCreate(BaseModel):
    title: str
    description: str
    image_s3_key: str
    has_length_option: bool
    gender_id: int
    length_id: Optional[int]
    order: int

class HairStyleUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    image_s3_key: Optional[str]
    has_length_option: Optional[bool]
    gender_id: Optional[int]
    length_id: Optional[int]
    order: Optional[int]


class HairStyleInDB(BaseModel):
    id: int
    title: str
    description: str
    image_s3_key: str
    has_length_option: bool
    gender_id: int
    order: int

    class Config:
        from_attributes=True