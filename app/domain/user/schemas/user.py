from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    provider: str
    social_id: str
    token: Optional[int] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    provider: Optional[str] = None
    social_id: Optional[str] = None
    token: Optional[int] = None
    deleted: Optional[bool] = None
    fcm_token: Optional[str] = None

class UserInDB(BaseModel):
    id: int
    uuid: str
    email: str
    provider: str
    social_id: str
    token: int
    deleted: bool
    fcm_token: str

    class Config:
        from_attributes=True