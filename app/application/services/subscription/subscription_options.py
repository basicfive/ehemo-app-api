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
        try:
            user_subs: List[UserSubscription] = self.user_sub_repo.get_all_by_user_with_plan(user_id=user_id)
            # 한 번이라도 구독 한 적이 있다면
            if user_subs:
                db_sub_plan_list = [
                    db_sub_plan for db_sub_plan in db_sub_plan_list
                    if db_sub_plan.plan_type != SubscriptionPlanType.FREE
                ]
        except NoResultFound:
            pass

        return [
            SubscriptionPlanInDB.model_validate(db_sub_plan)
            for db_sub_plan in db_sub_plan_list
        ]

def get_subscription_plan_query_service(
        subscription_plan_repo: SubscriptionPlanRepository = Depends(get_subscription_plan_repository),
        user_sub_repo: UserSubscriptionRepository = Depends(get_user_subscription_repository),
) -> SubscriptionPlanQueryService:
    return SubscriptionPlanQueryService(
        subscription_plan_repo=subscription_plan_repo,
        user_sub_repo=user_sub_repo,
    )

