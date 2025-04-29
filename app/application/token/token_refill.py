from datetime import datetime, UTC
from typing import List

from app import TokenTransactionConstants, FCMConstants
from app.application.transactional_service import TransactionalService
from app.core.db.base import get_db
from app.domain import User, BillingInterval
from app.domain.subscription.models.enums.subscription import SubscriptionPlanType
from app.domain.token.models.token import TokenWallet
from app.domain.token.services.refill import calculate_next_refill_date
from app.domain.token.enums.token import TokenSourceType
from app.domain.token.services.token_domain_sevice import TokenService, get_token_service
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.fcm.fcm_service import FCMService, get_fcm_service
from app.infrastructure.repositories.subscription.subscription import UserSubscriptionRepository, \
    get_user_subscription_repository
from app.infrastructure.repositories.token.token import get_token_wallet_repository, get_token_transaction_repository


class TokenRefillApplicationService(TransactionalService):
    def __init__(
            self,
            token_domain_service: TokenService,
            user_sub_repo: UserSubscriptionRepository,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.token_domain_service = token_domain_service
        self.user_sub_repo = user_sub_repo
        self.fcm_service = fcm_service

    @transactional
    def refill_tokens(self):
        current_time: datetime = datetime.now(UTC)
        active_subs_with_relations = (
            self.user_sub_repo.get_active_subscriptions_for_refill_with_relations(current_time)
        )

        # 유료 연간 플랜만 가져오기
        active_subs_with_relations = [
            sub for sub in active_subs_with_relations
            if sub.subscription_plan.billing_interval == BillingInterval.YEARLY
        ]

        for subscription in active_subs_with_relations:

            wallet: TokenWallet = subscription.token_wallet
            refill_amount = subscription.subscription_plan.tokens_per_period

            # 다음 리필 날짜 계산
            next_refill_date: datetime = calculate_next_refill_date(
                timezone=subscription.user.timezone,
                current_time=current_time,
                initial_purchase_time=subscription.initial_purchase_date,
            )

            self.token_domain_service.refill_token(
                token_wallet=wallet,
                amount=refill_amount,
                next_refill_date=next_refill_date,
                current_time=current_time,
                source_type=TokenSourceType.SUBSCRIPTION_RENEWAL,
            )

        # FCM 알림 발송
        self._send_refill_notifications(users=[sub.user for sub in active_subs_with_relations])

    def _send_refill_notifications(self, users: List[User]):
        fcm_tokens = [user.fcm_token for user in users if user.fcm_token]
        if fcm_tokens:
            self.fcm_service.send_to_tokens(
                tokens=fcm_tokens,
                title=FCMConstants.TOKEN_REFILL_TITLE,
                body=FCMConstants.TOKEN_REFILL_BODY,
            )


def refill_user_tokens():
    db = next(get_db())
    try:
        service = TokenRefillApplicationService(
            token_domain_service=get_token_service(
                token_wallet_repo=get_token_wallet_repository(db),
                token_transaction_repo=get_token_transaction_repository(db),
            ),
            user_sub_repo=get_user_subscription_repository(db),
            fcm_service=get_fcm_service(),
            unit_of_work=get_unit_of_work(db),
        )
        service.refill_tokens()
    finally:
        db.close()