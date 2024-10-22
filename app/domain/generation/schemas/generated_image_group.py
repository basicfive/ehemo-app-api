from typing import Optional
from pydantic import BaseModel

class GeneratedImageGroupCreate(BaseModel):
    user_id: int
    generation_request_id: int

class GeneratedImageGroupUpdate(BaseModel):
    user_id: Optional[int]
    generation_request_id: Optional[int]

class GeneratedImageGroupInDB(BaseModel):
    id:int
    user_id: int
    generation_request_id: int

    class Config:
        from_attributes=True