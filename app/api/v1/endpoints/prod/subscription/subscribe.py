from fastapi import APIRouter, status, Depends

from app.application.services.subscription.dto.subscription import UserSubscriptionInfo
from app.application.services.subscription.user_subscribe import UserSubscribeApplicationService, \
    get_subscription_application_service
from app.application.services.user.auth import validate_user_token

router = APIRouter()

# /prod/subscription/

@router.post("/subscribe/free-plan", response_model=UserSubscriptionInfo, status_code=status.HTTP_200_OK)
def create_free_plan(
        subscription_plan_id: int,
        user_id: int = Depends(validate_user_token),
        service: UserSubscribeApplicationService = Depends(get_subscription_application_service),
) -> UserSubscriptionInfo:
    return service.create_user_sub(subscription_plan_id, user_id)


# revenue cat webhook
# @router.post("/subscribe/paid-plan", status_code=status.HTTP_200_OK)
# # auth 검증 로직 추가해야함.
# def handle_revenuecat_webhook(
#         event_type: str,
#
# ):
#     event = RevenueCatEventType.from_str(event_type)
#
#     match event:
#         case RevenueCatEventType.INITIAL_PURCHASE:
#
#         case RevenueCatEventType.RENEWAL:
#
#         case RevenueCatEventType.EXPIRATION:
