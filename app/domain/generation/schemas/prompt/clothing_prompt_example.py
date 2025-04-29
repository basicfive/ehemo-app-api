from pydantic import BaseModel

class ClothingPromptExampleCreate(BaseModel):
    prompt: str

class ClothingPromptExampleUpdate(BaseModel):
    prompt: str

class ClothingPromptExampleInDB(BaseModel):
    id: int
    prompt: str

    class Config:
        from_attributes = True
