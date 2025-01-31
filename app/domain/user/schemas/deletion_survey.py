from typing import Optional
from pydantic import BaseModel

class ReasonOfDeletionCreate(BaseModel):
    reason: str
    follow_up_question: str

class ReasonOfDeletionUpdate(BaseModel):
    reason: Optional[str] = None
    follow_up_question: Optional[str] = None

class CustomReasonOfDeletionCreate(BaseModel):
    reason: str
    user_id: int

class CustomReasonOfDeletionUpdate(BaseModel):
    reason: Optional[str] = None
    user_id: Optional[int] = None

class FollowUpAnswerCreate(BaseModel):
    answer: str
    reason_id: int

class FollowUpAnswerUpdate(BaseModel):
    answer: Optional[str] = None
    reason_id: Optional[int] = None

class UserFollowUpAnswerCreate(BaseModel):
    user_id: int
    reason_id: int
    answer_id: int
    custom_answer: Optional[str]

class UserFollowUpAnswerUpdate(BaseModel):
    user_id: Optional[int] = None
    reason_id: Optional[int] = None
    answer_id: Optional[int] = None
    custom_answer: Optional[str] = None

