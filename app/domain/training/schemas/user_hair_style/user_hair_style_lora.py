from pydantic import BaseModel

class UserHairStyleLoraCreate(BaseModel):
    training_request_id: int
    user_id: int
    lora_name: str
    lora_s3_key: str

class UserHairStyleLoraUpdate(BaseModel):
    pass

class UserHairStyleLoraInDB(BaseModel):
    id: int
    training_request_id: int
    user_id: int
    lora_name: str
    lora_s3_key: str

    class Config:
        from_attributes = True
