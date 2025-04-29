from pydantic import BaseModel

class RequestPromptComponentQuestionAnswerCreate(BaseModel):
    generation_request_id: int
    prompt_component_question_id: int
    answer: str

class RequestPromptComponentQuestionAnswerUpdate(BaseModel):
    pass

class RequestPromptComponentQuestionAnswerInDB(BaseModel):
    id: int
    generation_request_id: int
    prompt_component_question_id: int
    answer: str

    class Config:
        from_attributes = True
