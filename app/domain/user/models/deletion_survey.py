from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.domain import TimeStampModel


class ReasonOfDeletion(TimeStampModel):
    __tablename__ = "reason_of_deletion"
    reason = Column(String, nullable=False)
    follow_up_question = Column(String, nullable=False)
    follow_up_question_description = Column(String, nullable=True)

class CustomReasonOfDeletion(TimeStampModel):
    __tablename__ = "custom_reason_of_deletion"
    user_id = Column(ForeignKey("user.id"), nullable=False)
    reason = Column(String, nullable=False)

class FollowUpAnswer(TimeStampModel):
    __tablename__ = "follow_up_answer"
    answer = Column(String, nullable=False)
    is_custom = Column(Boolean, default=False, nullable=False)

    reason_id = Column(ForeignKey("reason_of_deletion.id"), nullable=False)

    reason = relationship("ReasonOfDeletion")

class UserFollowUpAnswer(TimeStampModel):
    __tablename__ = "user_follow_up_answer"
    user_id = Column(ForeignKey("user.id"), nullable=False)
    reason_id = Column(ForeignKey("reason_of_deletion.id"), nullable=False)
    answer_id = Column(ForeignKey("follow_up_answer.id"), nullable=False)

    custom_answer = Column(String, nullable=True)

    user = relationship("User")
    reason = relationship("ReasonOfDeletion")
    answer = relationship("FollowUpAnswer")
