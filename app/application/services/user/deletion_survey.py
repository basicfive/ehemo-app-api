from typing import List
from fastapi import Depends

from app.application.services.transactional_service import TransactionalService
from app.application.services.user.dto.deletion_survey import ReasonOfDeletionDto, FollowUpAnswerDto, \
    UserFollowUpAnswerRequest
from app.domain import ReasonOfDeletion, FollowUpAnswer
from app.domain.user.schemas.deletion_survey import UserFollowUpAnswerCreate, CustomReasonOfDeletionCreate
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.user.deletion_survey import ReasonOfDeletionRepository, \
    FollowUpAnswerRepository, UserFollowUpAnswerRepository, get_reason_of_deletion_repository, \
    get_follow_up_answer_repository, get_user_follow_up_answer_repository, CustomReasonOfDeletionRepository, \
    get_custom_reason_of_deletion_repository


class UserDeletionSurveyService(TransactionalService):
    def __init__(
            self,
            reason_of_deletion_repo: ReasonOfDeletionRepository,
            custom_reason_of_deletion_repo: CustomReasonOfDeletionRepository,
            follow_up_answer_repo: FollowUpAnswerRepository,
            user_follow_up_answer_repo: UserFollowUpAnswerRepository,
            unit_of_work: UnitOfWork
    ):
        super().__init__(unit_of_work)
        self.reason_of_deletion_repo = reason_of_deletion_repo
        self.custom_reason_of_deletion_repo = custom_reason_of_deletion_repo
        self.follow_up_answer_repo = follow_up_answer_repo
        self.user_follow_up_answer_repo = user_follow_up_answer_repo

    def get_all_reasons_of_deletion(self) -> List[ReasonOfDeletionDto]:
        reasons: List[ReasonOfDeletion] = self.reason_of_deletion_repo.get_all()
        return sorted([ReasonOfDeletionDto.model_validate(reason) for reason in reasons], key=lambda x: x.id)

    def get_follow_up_answers(self, question_id: int) -> List[FollowUpAnswerDto]:
        answers: List[FollowUpAnswer] = self.follow_up_answer_repo.get_by_question(question_id)
        return sorted([FollowUpAnswerDto.model_validate(answer) for answer in answers], key=lambda x: x.id)

    @transactional
    def save_user_custom_reason(self, user_id: int, custom_reason: str):
        self.custom_reason_of_deletion_repo.create(
            obj_in=CustomReasonOfDeletionCreate(
                reason=custom_reason,
                user_id=user_id,
            )
        )

    @transactional
    def save_user_follow_up_answer(self, user_id: int, request: UserFollowUpAnswerRequest):
        for answer in request.answers:
            self.user_follow_up_answer_repo.create(
                obj_in=UserFollowUpAnswerCreate(
                    user_id=user_id,
                    reason_id=request.reason_id,
                    answer_id=answer.answer_id,
                    custom_answer=answer.custom_answer,
                )
            )

def get_user_deletion_survey_service(
        reason_of_deletion_repo: ReasonOfDeletionRepository = Depends(get_reason_of_deletion_repository),
        custom_reason_of_deletion_repo: CustomReasonOfDeletionRepository = Depends(get_custom_reason_of_deletion_repository),
        follow_up_answer_repo: FollowUpAnswerRepository = Depends(get_follow_up_answer_repository),
        user_follow_up_answer_repo: UserFollowUpAnswerRepository = Depends(get_user_follow_up_answer_repository),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> UserDeletionSurveyService:
    return UserDeletionSurveyService(
        reason_of_deletion_repo=reason_of_deletion_repo,
        custom_reason_of_deletion_repo=custom_reason_of_deletion_repo,
        follow_up_answer_repo=follow_up_answer_repo,
        user_follow_up_answer_repo=user_follow_up_answer_repo,
        unit_of_work=unit_of_work,
    )