from pydantic import BaseModel

class UserTokenResponse(BaseModel):
    token: int

class UserInfoResponse(BaseModel):
    uuid: str
    email: str
    token: int
