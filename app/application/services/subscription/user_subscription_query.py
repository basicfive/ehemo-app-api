from fastapi import Depends
from sqlalchemy.exc import NoResultFound

from app.application.services.subscription.dto.subscription import UserSubscriptionStatus, UserSubscriptionInfo
from app.domain import UserSubscription, SubscriptionPlan
from app.infrastructure.repositories.subscription.subscription import UserSubscriptionRepository, \
    get_user_subscription_repository


class UserSubscriptionQueryService:
    def __init__(
            self,
            user_sub_repo: UserSubscriptionRepository,
    ):
        self.user_sub_repo = user_sub_repo

    def get_user_subscription_status(self, user_id: int) -> UserSubscriptionStatus:
        try:
            user_sub_with_plan: UserSubscription = self.user_sub_repo.get_by_user_with_plan(user_id)
        except NoResultFound:
            return UserSubscriptionStatus(is_subscribed=False)

        subscription_plan: SubscriptionPlan = user_sub_with_plan.subscription_plan

        return UserSubscriptionStatus(
            is_subscribed=True,
            info=UserSubscriptionInfo(
                original_transaction_id=user_sub_with_plan.original_transaction_id,
                plan_type=subscription_plan.plan_type,
                name=subscription_plan.name,
                description=subscription_plan.description,
                next_billing_date=user_sub_with_plan.expire_date,
            )
        )

def get_user_subscription_query_service(
        user_sub_repo: UserSubscriptionRepository = Depends(get_user_subscription_repository),
) -> UserSubscriptionQueryService:
    return UserSubscriptionQueryService(
        user_sub_repo=user_sub_repo,
    )
