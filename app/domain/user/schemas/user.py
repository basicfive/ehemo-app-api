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

class UserInDB(BaseModel):
    id: int
    email: str
    provider: str
    social_id: str
    token: int

    class Config:
        from_attributes=True