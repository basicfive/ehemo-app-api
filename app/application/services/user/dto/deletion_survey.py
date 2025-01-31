from typing import Optional, List
from pydantic import BaseModel

class ReasonOfDeletionDto(BaseModel):
    id: int
    reason: str
    follow_up_question: str
    follow_up_question_description: Optional[str]

    class Config:
        from_attributes=True

class FollowUpAnswerDto(BaseModel):
    id: int
    answer: str
    is_custom: bool

    class Config:
        from_attributes=True

class UserFollowUpAnswerDto(BaseModel):
    answer_id: int
    custom_answer: Optional[str]

class UserFollowUpAnswerRequest(BaseModel):
    reason_id: int
    answers: List[UserFollowUpAnswerDto]
