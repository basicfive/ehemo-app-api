from pydantic import BaseModel
from datetime import datetime
from app.domain.subscription.models.enums.subscription import StoreType

class StoreProductCreate(BaseModel):
    pass

class StoreProductUpdate(BaseModel):
    pass

class StoreProductInDB(BaseModel):
    
    id: int
    store_type: StoreType
    product_id: str
    price: float
    token_amount: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True