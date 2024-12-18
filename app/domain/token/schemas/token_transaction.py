from typing import Optional
from pydantic import BaseModel

from app.domain.token.models.enums.token import TokenTransactionType, TokenSourceType

class TokenTransactionCreate(BaseModel):
    transaction_type: TokenTransactionType
    source_type: TokenSourceType
    amount: int

    balance_before: int
    balance_after: int

    description: Optional[str]

    token_wallet_id: int

class TokenTransactionUpdate(BaseModel):
    transaction_type: Optional[TokenTransactionType] = None
    source_type: Optional[TokenSourceType] = None
    amount: Optional[int] = None

    balance_before: Optional[int] = None
    balance_after: Optional[int] = None

    description: Optional[str] = None

class TokenTransactionInDB(BaseModel):
    id: int

    transaction_type: TokenTransactionType
    source_type: TokenSourceType
    amount: int

    balance_before: int
    balance_after: int

    description: Optional[str]

    token_wallet_id: int

    class Config:
        from_attributes=True