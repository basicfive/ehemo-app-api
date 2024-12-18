from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TokenWalletCreate(BaseModel):
    remaining_token: int
    total_received_tokens: Optional[int]

    next_refill_date: datetime
    last_refill_date: datetime

    user_id: int
    user_subscription_id: int


class TokenWalletUpdate(BaseModel):
    remaining_token: Optional[int] = None
    total_received_tokens: Optional[int] = None

    next_refill_date: Optional[datetime] = None
    last_refill_date: Optional[datetime] = None

    user_id: Optional[int] = None
    user_subscription_id: Optional[int] = None


class TokenWalletInDB(BaseModel):
    id: int
    remaining_token: int
    total_received_tokens: int

    next_refill_date: datetime
    last_refill_date: datetime

    user_id: int
    user_subscription_id: int

    class Config:
        from_attributes=True
