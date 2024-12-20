from fastapi import APIRouter, status, Depends

from app.application.services.subscription.dto.subscription_status import UserSubscriptionStatus
from app.application.services.subscription.free_subscription import FreeSubscriptionApplicationService, \
    get_free_subscription_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# /prod/subscription/

@router.post("/subscribe/free-plan", response_model=UserSubscriptionStatus, status_code=status.HTTP_200_OK)
def create_free_plan(
        subscription_plan_id: int,
        user_id: int = Depends(validate_user_token),
        service: FreeSubscriptionApplicationService = Depends(get_free_subscription_application_service),
) -> UserSubscriptionStatus:
    return service.create_user_sub(subscription_plan_id, user_id)

