from typing import List
from fastapi import Depends

from app.domain import SubscriptionPlan
from app.domain.subscription.models.enums.subscription import StoreType
from app.domain.subscription.schemas.subscription_plan import SubscriptionPlanInDB
from app.infrastructure.repositories.subscription.subscription import SubscriptionPlanRepository, \
    get_subscription_plan_repository


class SubscriptionPlanQueryService:
    def __init__(
            self,
            subscription_plan_repo: SubscriptionPlanRepository,
    ):
        self.subscription_plan_repo = subscription_plan_repo

    def get_all_sub_plans_by_store_type(self, store_type: StoreType) -> List[SubscriptionPlanInDB]:
        db_sub_plan_list: List[SubscriptionPlan] = self.subscription_plan_repo.get_all_by_store_type(store_type)
        return [
            SubscriptionPlanInDB.model_validate(db_sub_plan)
            for db_sub_plan in db_sub_plan_list
        ]

def get_subscription_plan_query_service(
        subscription_plan_repo: SubscriptionPlanRepository = Depends(get_subscription_plan_repository),
) -> SubscriptionPlanQueryService:
    return SubscriptionPlanQueryService(
        subscription_plan_repo=subscription_plan_repo,
    )

