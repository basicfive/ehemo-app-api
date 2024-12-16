from fastapi import APIRouter, status, Depends

from app.application.services.subscription.dto.subscription import FreePlanSubRequest
from app.application.services.subscription.subscription import SubscriptionApplicationService, \
    get_subscription_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# /prod/subscription/

@router.post("/free-plan", status_code=status.HTTP_200_OK)
def create_free_plan(
        request: FreePlanSubRequest,
        user_id: int = Depends(validate_user_token),
        service: SubscriptionApplicationService = Depends(get_subscription_application_service),
):
    service.create_free_plan(request, user_id)