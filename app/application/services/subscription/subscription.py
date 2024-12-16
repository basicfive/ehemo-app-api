from fastapi import Depends
from uuid import uuid4
from datetime import datetime, UTC

from app.application.services.subscription.dto.subscription import FreePlanSubRequest, SubResponse
from app.application.services.transactional_service import TransactionalService
from app.core.config import token_setting
from app.domain.subscription.models.enums.subscription import SubscriptionPlanType, SubscriptionStatus
from app.domain.subscription.models.subscription import Subscription
from app.domain.subscription.schemas.subscription import SubscriptionCreate, SubscriptionInDB
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.subscription.subscription import SubscriptionRepository, \
    get_subscription_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class SubscriptionApplicationService(TransactionalService):
    def __init__(
            self,
            subscription_repo: SubscriptionRepository,
            user_repo: UserRepository,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo

    # 웹훅으로 처리해야하는 api

    # 무료 구독 api
    # TODO: timezone config 사용?
    def create_free_plan(self, request: FreePlanSubRequest, user_id: int):
        db_subscription: Subscription = self.subscription_repo.create_with_flush(
            obj_in=SubscriptionCreate(
                original_transaction_id=str(uuid4()),
                store=None,
                token=token_setting.FREE_TRIAL_TOKEN,
                timezone=request.timezone,
                next_token_refill_date=datetime.now(UTC),
                expire_date=datetime.now(UTC),
                plan_type=SubscriptionPlanType.FREE,
                billing_interval=None,
                subscription_status=SubscriptionStatus.ACTIVE,
                user_id=user_id,
            )
        )
        subscription = SubscriptionInDB.model_validate(db_subscription)
        return SubResponse(
            **subscription.model_dump()
        )

def get_subscription_application_service(
        subscription_repo: SubscriptionRepository = Depends(get_subscription_repository),
        user_repo: UserRepository = Depends(get_user_repository),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> SubscriptionApplicationService:
    return SubscriptionApplicationService(
        subscription_repo=subscription_repo,
        user_repo=user_repo,
        unit_of_work=unit_of_work,
    )