from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: str

class UserInDB(BaseModel):
    id: int
    token: int

    class Config:
        from_attributes=True