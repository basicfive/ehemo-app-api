from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserTokenResponse(BaseModel):
    token: int

class TokenHistory(BaseModel):
    amount: int
    balance_after: int
    description: Optional[str]

    transaction_date: datetime

