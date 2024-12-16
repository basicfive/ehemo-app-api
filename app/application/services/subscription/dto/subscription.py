from pydantic import BaseModel

class FreePlanSubRequest(BaseModel):
    timezone: str

class SubResponse(BaseModel):
    original_transaction_id: str
