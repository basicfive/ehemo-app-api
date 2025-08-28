from pydantic import BaseModel

class StoreProductDto(BaseModel):
    id: int
    store_type: str
    product_id: str
    price: float
    token_amount: int
    
