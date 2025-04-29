from pydantic import BaseModel

class PosePromptExampleCreate(BaseModel):
    prompt: str

class PosePromptExampleUpdate(BaseModel):
    prompt: str

class PosePromptExampleInDB(BaseModel):
    id: int
    prompt: str

    class Config:
        from_attributes = True
