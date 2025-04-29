from pydantic import BaseModel


class LengthPromptEnhancementCreate(BaseModel):
    pass

class LengthPromptEnhancementUpdate(BaseModel):
    pass

class LengthPromptEnhancementInDB(BaseModel):
    keyword: str
    enhance_prompt: str

    class Config:
        from_attributes = True