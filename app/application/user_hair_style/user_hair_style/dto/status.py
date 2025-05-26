from pydantic import BaseModel
from datetime import datetime

from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus

class RegisterStatus(BaseModel):
    user_hair_style_id: int
    status: UserHairStyleStatus
    expires_at: datetime