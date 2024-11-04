from pydantic import BaseModel

class UserTokenResponse(BaseModel):
    token: int