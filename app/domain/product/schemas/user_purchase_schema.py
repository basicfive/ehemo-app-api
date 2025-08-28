from pydantic import BaseModel
from datetime import datetime


class UserPurchaseCreate(BaseModel):
    user_id: int
    store_product_id: int
    price_paid: float
    price_paid_in_purchased_currency: float
    received_token_amount: int
    transaction_id: str

class UserPurchaseUpdate(BaseModel):
    pass


class UserPurchaseInDB(BaseModel):
    id: int
    user_id: int
    store_product_id: int
    price_paid: float
    price_paid_in_purchased_currency: float
    received_token_amount: int
    transaction_id: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True