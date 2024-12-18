from fastapi import Depends
from uuid import uuid4
from datetime import datetime, UTC
from dateutil.relativedelta import relativedelta

from app import token_settings
from app.application.services.subscription.dto.subscription import UserSubscriptionInfo
from app.application.services.transactional_service import TransactionalService
from app.domain import SubscriptionPlan
from app.domain.subscription.models.enums.subscription import SubscriptionStatus
from app.domain.subscription.models.subscription import UserSubscription
from app.domain.subscription.schemas.user_subscription import UserSubscriptionCreate, UserSubscriptionInDB
from app.domain.token.schemas.token_wallet import TokenWalletCreate
from app.domain.token.services.token_domain_sevice import TokenDomainService, get_token_domain_service
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.subscription.subscription import UserSubscriptionRepository, \
    get_user_subscription_repository, SubscriptionPlanRepository, get_subscription_plan_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class UserSubscribeApplicationService(TransactionalService):
    def __init__(
            self,
            user_sub_repo: UserSubscriptionRepository,
            subscription_plan_repo: SubscriptionPlanRepository,
            token_domain_service: TokenDomainService,
            user_repo: UserRepository,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_sub_repo = user_sub_repo
        self.subscription_plan_repo = subscription_plan_repo
        self.token_domain_service = token_domain_service
        self.user_repo = user_repo

    # 웹훅으로 처리해야하는 api


    # TODO: timezone config 사용?
    # 무료 구독 api
    @transactional
    def create_user_sub(self, subscription_plan_id: int, user_id: int) -> UserSubscriptionInfo:

        # TODO: 이미 구독이 있는 경우에는 validation

        # user sub 생성
        current_datetime: datetime = datetime.now(UTC)
        hundred_years_later: datetime = current_datetime + relativedelta(years=100)

        subscription_plan: SubscriptionPlan = self.subscription_plan_repo.get(subscription_plan_id)
        new_transaction_id: str = str(uuid4())

        db_user_sub: UserSubscription = self.user_sub_repo.create_with_flush(
            obj_in=UserSubscriptionCreate(
                original_transaction_id=new_transaction_id,
                latest_transaction_id=new_transaction_id,
                purchase_date=current_datetime,
                expire_date=hundred_years_later,
                status=SubscriptionStatus.ACTIVE,
                auto_renew_status=False,
                user_id=user_id,
                subscription_plan_id=subscription_plan_id,
            )
        )

        # token wallet 생성
        token_wallet = self.token_domain_service.create_wallet_with_flush(
            wallet_create=TokenWalletCreate(
                remaining_token=token_settings.FREE_TRIAL_TOKEN,
                total_received_tokens=token_settings.FREE_TRIAL_TOKEN,
                next_refill_date=hundred_years_later,
                last_refill_date=current_datetime,
                user_id=user_id,
                user_subscription_id=db_user_sub.id,
            )
        )

        user_sub = UserSubscriptionInDB.model_validate(db_user_sub)

        return UserSubscriptionInfo(
            original_transaction_id=user_sub.original_transaction_id,
            plan_type=subscription_plan.plan_type,
            name=subscription_plan.name,
            description=subscription_plan.description,
            next_billing_date=hundred_years_later,
        )

def get_subscription_application_service(
        user_sub_repo: UserSubscriptionRepository = Depends(get_user_subscription_repository),
        subscription_plan_repo: SubscriptionPlanRepository = Depends(get_subscription_plan_repository),
        token_domain_service: TokenDomainService = Depends(get_token_domain_service),
        user_repo: UserRepository = Depends(get_user_repository),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> UserSubscribeApplicationService:
    return UserSubscribeApplicationService(
        user_sub_repo=user_sub_repo,
        subscription_plan_repo=subscription_plan_repo,
        token_domain_service=token_domain_service,
        user_repo=user_repo,
        unit_of_work=unit_of_work,
    )