from pydantic import BaseModel

from app.domain.generation.enums.prompt_component import PromptComponentType

class PromptComponentQuestionCreate(BaseModel):
    component_type: PromptComponentType
    question: str
    order: int

class PromptComponentQuestionUpdate(BaseModel):
    pass

class PromptComponentQuestionInDB(BaseModel):
    id: int
    component_type: PromptComponentType
    question: str
    order: int

    class Config:
        from_attributes = True
