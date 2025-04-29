from typing import List
from fastapi import APIRouter, Depends, status

from app.application.user.auth import validate_user_token
from app.application.user.deletion_survey import UserDeletionSurveyService, get_user_deletion_survey_service
from app.application.user.dto.deletion_survey import ReasonOfDeletionDto, FollowUpAnswerDto, \
    UserFollowUpAnswerRequest

router = APIRouter()

# /prod/user/

@router.get("/reasons-of-deletion", response_model=List[ReasonOfDeletionDto], status_code=status.HTTP_200_OK)
def get_reasons_of_deletion(
        _: int = Depends(validate_user_token),
        service: UserDeletionSurveyService = Depends(get_user_deletion_survey_service)
) -> List[ReasonOfDeletionDto]:
    return service.get_all_reasons_of_deletion()

@router.get("/follow-up-answers", response_model=List[FollowUpAnswerDto], status_code=status.HTTP_200_OK)
def get_follow_up_answers(
        reason_id: int,
        _: int = Depends(validate_user_token),
        service: UserDeletionSurveyService = Depends(get_user_deletion_survey_service)
) -> List[FollowUpAnswerDto]:
    return service.get_follow_up_answers(reason_id)

@router.post("/custom-reason-of-deletion", status_code=status.HTTP_200_OK)
def save_user_custom_reason(
        custom_reason: str,
        user_id: int = Depends(validate_user_token),
        service: UserDeletionSurveyService = Depends(get_user_deletion_survey_service)
):
    service.save_user_custom_reason(user_id=user_id, custom_reason=custom_reason)

@router.post("/user-survey-answer", status_code=status.HTTP_200_OK)
def save_user_follow_up_answer(
        request: UserFollowUpAnswerRequest,
        user_id: int = Depends(validate_user_token),
        service: UserDeletionSurveyService = Depends(get_user_deletion_survey_service)
):
    service.save_user_follow_up_answer(user_id=user_id, request=request)
