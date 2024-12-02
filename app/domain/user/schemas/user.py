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

class UserInDB(BaseModel):
    id: int
    email: str
    provider: str
    social_id: str
    token: int
    deleted: bool

    class Config:
        from_attributes=True