from typing import List, Optional
from fastapi import Depends
from sqlalchemy.exc import NoResultFound

from app.domain import SubscriptionPlan, UserSubscription, SubscriptionPlanType
from app.domain.subscription.models.enums.subscription import StoreType
from app.domain.subscription.schemas.subscription_plan import SubscriptionPlanInDB
from app.infrastructure.repositories.subscription.subscription import SubscriptionPlanRepository, \
    get_subscription_plan_repository, UserSubscriptionRepository, get_user_subscription_repository


class SubscriptionPlanQueryService:
    def __init__(
            self,
            subscription_plan_repo: SubscriptionPlanRepository,
            user_sub_repo: UserSubscriptionRepository,
    ):
        self.subscription_plan_repo = subscription_plan_repo
        self.user_sub_repo = user_sub_repo

    def get_sub_plans_by_store_type(self, store_type: StoreType, user_id: int) -> List[SubscriptionPlanInDB]:
        db_sub_plan_list: List[SubscriptionPlan] = self.subscription_plan_repo.get_all_by_store_type(store_type)
        exclude_plan_id: int = -1

        try:
            user_sub: UserSubscription = self.user_sub_repo.get_by_user_with_plan(user_id=user_id)
            # 무료 플랜 구독 중이라면
            sub_plan: SubscriptionPlan = user_sub.subscription_plan
            if sub_plan.plan_type == SubscriptionPlanType.FREE:
                exclude_plan_id = sub_plan.id
        except NoResultFound:
            pass

        return [
            SubscriptionPlanInDB.model_validate(db_sub_plan)
            for db_sub_plan in db_sub_plan_list
            if db_sub_plan.id != exclude_plan_id
        ]

def get_subscription_plan_query_service(
        subscription_plan_repo: SubscriptionPlanRepository = Depends(get_subscription_plan_repository),
        user_sub_repo: UserSubscriptionRepository = Depends(get_user_subscription_repository),
) -> SubscriptionPlanQueryService:
    return SubscriptionPlanQueryService(
        subscription_plan_repo=subscription_plan_repo,
        user_sub_repo=user_sub_repo,
    )

