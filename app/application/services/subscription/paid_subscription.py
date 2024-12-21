from fastapi import Depends

from app.application.services.subscription.dto.revenue_cat.event import *
from app.application.services.transactional_service import TransactionalService
from app.domain.token.services.token_domain_sevice import TokenDomainService, get_token_domain_service
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.subscription.subscription import UserSubscriptionRepository, \
    SubscriptionPlanRepository, get_subscription_plan_repository, get_user_subscription_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class PaidSubscriptionApplicationService(TransactionalService):
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

    # 초기 구매
    def handle_initial_purchase(self, event: InitialPurchase):
        print(event.model_dump())
        """초기 구매 이벤트 처리"""
        pass

    def handle_cancellation(self, event: Cancellation):
        print(event.model_dump())
        """구독 취소 이벤트 처리"""
        pass

    def handle_uncancellation(self, event: Uncancellation):
        print(event.model_dump())
        """구독 취소 철회 이벤트 처리"""
        pass

    def handle_renewal(self, event: Renewal):
        print(event.model_dump())
        """구독 갱신 이벤트 처리"""
        pass

    def handle_product_change(self, event: ProductChange):
        print(event.model_dump())
        """상품 변경 이벤트 처리"""
        pass

    def handle_expiration(self, event: Expiration):
        print(event.model_dump())
        pass

    # def handle_test_event(self, event: Test):
    #     print(event.model_dump())
    #     pass

def get_paid_subscription_application_service(
        user_sub_repo: UserSubscriptionRepository = Depends(get_user_subscription_repository),
        subscription_plan_repo: SubscriptionPlanRepository = Depends(get_subscription_plan_repository),
        token_domain_service: TokenDomainService = Depends(get_token_domain_service),
        user_repo: UserRepository = Depends(get_user_repository),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> PaidSubscriptionApplicationService:
    return PaidSubscriptionApplicationService(
        user_sub_repo=user_sub_repo,
        subscription_plan_repo=subscription_plan_repo,
        token_domain_service=token_domain_service,
        user_repo=user_repo,
        unit_of_work=unit_of_work,
    )
