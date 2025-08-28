from pydantic import BaseModel
class UserInfoResponse(BaseModel):
    uuid: str
    email: str
