from pydantic import BaseModel

class AuthInfo(BaseModel):
    provider: str
    social_id: str
    email: str