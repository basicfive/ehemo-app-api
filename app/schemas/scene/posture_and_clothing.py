from pydantic import BaseModel

class PostureAndClothingCreate(BaseModel):
    prompt: str
    gender_id: int

class PostureAndClothingUpdate(BaseModel):
    prompt: str
    gender_id: int

class PostureAndClothingInDB(BaseModel):
    id: int
    prompt: str
    gender_id: int
