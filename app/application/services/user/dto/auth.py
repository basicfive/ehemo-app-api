from pydantic import BaseModel

class UserInfo(BaseModel):
    provider: str
    social_id: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class LoginResponse(BaseModel):
    uuid: str
    email: str
    user_token: int
    access_token: str
    refresh_token: str