from pydantic import BaseModel

class UserInfo(BaseModel):
    email: str
    provider: str
    social_id: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
