from pydantic import BaseModel

class UserInfo(BaseModel):
    provider: str
    social_id: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
