from typing import List
from fastapi import APIRouter, Depends, status

from app.application.services.subscription.dto.subscription_status import UserSubscriptionInfo, UserSubscriptionStatus
from app.application.services.subscription.subscription_options import SubscriptionPlanQueryService, \
    get_subscription_plan_query_service
from app.application.services.subscription.user_subscription_query import UserSubscriptionQueryService, \
    get_user_subscription_query_service
from app.application.services.user.auth import validate_user_token
from app.domain import StoreType
from app.domain.subscription.schemas.subscription_plan import SubscriptionPlanInDB

router = APIRouter()

# /prod/subscription/

@router.get("/plans", response_model=List[SubscriptionPlanInDB], status_code=status.HTTP_200_OK)
def get_plan_options(
        store_type: StoreType,
        _: int = Depends(validate_user_token),
        service: SubscriptionPlanQueryService = Depends(get_subscription_plan_query_service),
) -> List[SubscriptionPlanInDB]:
    return service.get_all_sub_plans_by_store_type(store_type=store_type)


@router.get("/status", response_model=UserSubscriptionStatus, status_code=status.HTTP_200_OK)
def get_user_subscription_status(
        user_id: int = Depends(validate_user_token),
        service: UserSubscriptionQueryService = Depends(get_user_subscription_query_service),
) -> UserSubscriptionStatus:
    return service.get_user_subscription_status(user_id)