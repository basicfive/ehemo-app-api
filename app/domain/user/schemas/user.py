from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    provider: str
    social_id: str

class UserUpdate(BaseModel):
    fcm_token: Optional[str] = None

    email: Optional[str] = None
    provider: Optional[str] = None
    social_id: Optional[str] = None

    deleted: Optional[bool] = None

class UserInDB(BaseModel):
    id: int
    uuid: str
    fcm_token: str

    email: str
    provider: str
    social_id: str

    deleted: bool

    class Config:
        from_attributes=True