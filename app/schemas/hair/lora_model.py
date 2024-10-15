from typing import Optional
from pydantic import BaseModel

class LoRAModelCreate(BaseModel):
    prompt: str
    lora_model_description: str
    supported_style: Optional[str]
    supported_lengths: Optional[str]
    supported_colors: Optional[str]

class LoRAModelUpdate(BaseModel):
    prompt: Optional[str]
    lora_model_description: Optional[str]
    supported_style: Optional[str]
    supported_lengths: Optional[str]
    supported_colors: Optional[str]

class LoRAModelInDB(BaseModel):
    id: int
    prompt: str
    lora_model_description: str
    supported_style: Optional[str]
    supported_lengths: Optional[str]
    supported_colors: Optional[str]

    class Config:
        from_attributes=True
