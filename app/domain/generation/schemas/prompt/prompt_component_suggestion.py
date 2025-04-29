from pydantic import BaseModel

class PromptComponentSuggestionCreate(BaseModel):
    suggestion: str
    order: int
    question_id: int

class PromptComponentSuggestionUpdate(BaseModel):
    pass

class PromptComponentSuggestionInDB(BaseModel):
    id: int
    suggestion: str
    order: int
    question_id: int

    class Config:
        from_attributes = True
