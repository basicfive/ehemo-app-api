from datetime import datetime, UTC
from typing import List

from app.application.services.transactional_service import TransactionalService
from app.core.config import token_setting, fcm_setting
from app.core.db.base import get_db
from app.domain.subscription.models.subscription import Subscription
from app.domain.subscription.schemas.subscription import SubscriptionUpdate
from app.domain.subscription.services.token import calculate_next_refill_date
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.fcm.fcm_service import FCMService, get_fcm_service
from app.infrastructure.repositories.subscription.subscription import SubscriptionRepository, \
    get_subscription_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class TokenRefillApplicationService(TransactionalService):
    def __init__(
            self,
            subscription_repo: SubscriptionRepository,
            user_repo: UserRepository,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        self.fcm_service = fcm_service

    # TODO: 다국어 지원(다국적 지원)하게 되면 리프레시 타이밍을 매 시간마다로 변경해줘야함.
    @transactional
    def refill_tokens(self):
        current_time: datetime = datetime.now(UTC)
        to_refill: List[Subscription] = (
            self.subscription_repo.get_subscriptions_for_token_refresh(current_time=current_time)
        )

        for subscription in to_refill:
            self.subscription_repo.update(
                obj_id=subscription.id,
                obj_in=SubscriptionUpdate(
                    token=token_setting.MONTHLY_REFILLED_TOKEN,
                    next_token_refill_date=calculate_next_refill_date(subscription.timezone)
                )
            )

        # 토큰 리필됐음 알리는 push 전송
        user_ids = [sub.user_id for sub in to_refill]
        users = self.user_repo.get_users_by_ids(user_ids)

        fcm_tokens = [user.fcm_token for user in users if user.fcm_token]

        if fcm_tokens:
            self.fcm_service.send_to_tokens(
                tokens=fcm_tokens,
                title=fcm_setting.TOKEN_REFILL_TITLE,
                body=fcm_setting.TOKEN_REFILL_BODY,
            )

def refill_user_tokens():
    db = next(get_db())
    try:
        service = TokenRefillApplicationService(
            subscription_repo=get_subscription_repository(db),
            user_repo=get_user_repository(db),
            fcm_service=get_fcm_service(),
            unit_of_work=get_unit_of_work(db),
        )
        service.refill_tokens()
    finally:
        db.close()