from pydantic import BaseModel

class HairStyleLoraCreate(BaseModel):
    lora_name: str
    lora_s3_key: str

class HairStyleLoraUpdate(BaseModel):
    pass

class HairStyleLoraInDB(BaseModel):
    id: int
    lora_name: str
    lora_s3_key: str

    class Config:
        from_attributes = True
