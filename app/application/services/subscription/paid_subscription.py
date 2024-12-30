from fastapi import Depends
from datetime import datetime
import logging

from sqlalchemy.exc import NoResultFound

from app.application.services.subscription.dto.revenue_cat.event import *
from app.application.services.transactional_service import TransactionalService
from app.core.errors.http_exceptions import RevenuecatWebhookException
from app.core.utils import ms_to_datetime
from app.domain import User, SubscriptionPlan, SubscriptionStatus, UserSubscription, TokenWallet, TokenSourceType
from app.domain.subscription.schemas.user_subscription import UserSubscriptionCreate, UserSubscriptionUpdate
from app.domain.token.services.refill import calculate_next_refill_date
from app.domain.token.services.token_domain_sevice import TokenDomainService, get_token_domain_service
from app.infrastructure.database.transaction import transactional
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
        self.logger = logging.getLogger(__name__)

    def _validate_initial_purchase_event(self, event: InitialPurchase):
        try:
            user_sub: UserSubscription = (
                self.user_sub_repo.get_active_sub_by_og_transaction_id(event.original_transaction_id)
            )
            self.logger.error("Activate user subscription with same original_transaction_id exists.")
            self.logger.error(
                f"original_transaction_id: {event.original_transaction_id}\n"
                f"user_id: {user_sub.user_id}\n"
                f"app_user_id: {event.app_user_id}"
            )
            raise RevenuecatWebhookException()
        except NoResultFound:
            pass

    def _get_user_sub_with_validation(self, event: BaseEvent) -> UserSubscription:
        try:
            user_sub: UserSubscription = (
                self.user_sub_repo.get_active_sub_by_og_transaction_id(event.original_transaction_id)
            )
        except NoResultFound:
            self.logger.error(
                f"There is no active user subscription with original_transaction_id: {event.original_transaction_id}"
            )
            raise RevenuecatWebhookException()
        return user_sub

    def _get_user_sub_with_relations(self, event: BaseEvent) -> UserSubscription:
        try:
            user_sub: UserSubscription = (
                self.user_sub_repo.get_by_og_transaction_id_current_sub_with_relations(event.original_transaction_id)
            )
        except NoResultFound:
            self.logger.error(
                f"There is no active user subscription with original_transaction_id: {event.original_transaction_id}"
            )
            raise RevenuecatWebhookException()
        return user_sub

    def _create_new_subscription_for_user(self, user: User, event: BaseEvent):
        subscription_plan: SubscriptionPlan = self.subscription_plan_repo.get_by_product_id(event.product_id)
        purchase_date: datetime = ms_to_datetime(event.purchased_at_ms)

        next_refill_date = calculate_next_refill_date(
            user.timezone,
            purchase_date,
            purchase_date,
        )

        user_sub: UserSubscription = self.user_sub_repo.create_with_flush(
            obj_in=UserSubscriptionCreate(
                original_transaction_id=event.original_transaction_id,
                latest_transaction_id=event.transaction_id,
                initial_purchase_date=ms_to_datetime(event.purchased_at_ms),
                purchase_date=ms_to_datetime(event.purchased_at_ms),
                expire_date=ms_to_datetime(event.expiration_at_ms),
                status=SubscriptionStatus.ACTIVE,
                user_id=user.id,
                subscription_plan_id=subscription_plan.id,
            )
        )

        self.token_domain_service.create_and_init_wallet(
            fill_amount=subscription_plan.tokens_per_period,
            user_id=user.id,
            user_subscription_id=user_sub.id,
            next_refill_date=next_refill_date,
            current_time=purchase_date,
        )

    # 초기 구매
    @transactional
    def handle_initial_purchase(self, event: InitialPurchase):
        # 이미 존재하는 original_transaction_id 값이 있다면 걸러야함.
        self._validate_initial_purchase_event(event=event)

        try:
            user: User = self.user_repo.get_by_uuid(event.app_user_id)
        except NoResultFound:
            self.logger.error(
                f"Initial Purchase Event error\n"
                f"Cannot find user matching given user uuid from event\n"
            )
            raise RevenuecatWebhookException()

        self._create_new_subscription_for_user(user=user, event=event)


    @transactional
    def handle_renewal(self, event: Renewal):
        """구독 갱신 이벤트 처리"""
        user_sub_with_relations = self._get_user_sub_with_relations(event)

        subscription_plan: SubscriptionPlan = user_sub_with_relations.subscription_plan
        token_wallet: TokenWallet = user_sub_with_relations.token_wallet
        user: User = user_sub_with_relations.user
        purchase_date: datetime = ms_to_datetime(event.purchased_at_ms)

        if user_sub_with_relations.subscription_plan.product_id != event.product_id:
            # PRODUCT CHANGE 하고 RENEW 로 이벤트 오는 경우
            self._handle_product_change(user_sub_with_relations=user_sub_with_relations, event=event)
            return
        if user_sub_with_relations.status == SubscriptionStatus.EXPIRED:
            # EXPIRED -> RENEW 로 다시 구매한 유저에 대한 처리
            self._handle_resubscription(user_sub_with_relations=user_sub_with_relations, event=event)
            return

        self.user_sub_repo.update(
            obj_id=user_sub_with_relations.id,
            obj_in=UserSubscriptionUpdate(
                latest_transaction_id=event.transaction_id,
                purchase_date=purchase_date,
                expire_date=ms_to_datetime(event.expiration_at_ms),
            )
        )

        next_refill_date = calculate_next_refill_date(
            user.timezone,
            purchase_date,
            user_sub_with_relations.initial_purchase_date,
        )

        # 토큰 업데이트
        self.token_domain_service.refill_token(
            token_wallet=token_wallet,
            amount=subscription_plan.tokens_per_period,
            next_refill_date=next_refill_date,
            current_time=purchase_date,
            source_type=TokenSourceType.SUBSCRIPTION_RENEWAL,
        )

    def _handle_product_change(
            self,
            user_sub_with_relations: UserSubscription,
            event: Renewal
    ):
        """PRODUCT CHANGE 하고 RENEW 로 이벤트 오는 경우"""
        user: User = user_sub_with_relations.user

        self.user_sub_repo.update(
            obj_id=user_sub_with_relations.id,
            obj_in=UserSubscriptionUpdate(
                status=SubscriptionStatus.CHANGED
            )
        )

        self._create_new_subscription_for_user(user=user, event=event)

    def _handle_resubscription(
            self,
            user_sub_with_relations: UserSubscription,
            event: Renewal
    ):
        """EXPIRED -> RENEW 로 다시 구매한 유저에 대한 처리"""
        self._create_new_subscription_for_user(user=user_sub_with_relations.user, event=event)


    @transactional
    def handle_cancellation(self, event: Cancellation):
        """구독 취소 이벤트 처리"""
        user_sub = self._get_user_sub_with_validation(event)

        self.user_sub_repo.update(
            obj_id=user_sub.id,
            obj_in=UserSubscriptionUpdate(
                status=SubscriptionStatus.CANCELED,
                latest_transaction_id=event.transaction_id,
            )
        )

    @transactional
    def handle_uncancellation(self, event: Uncancellation):
        """구독 취소 철회 이벤트 처리"""
        user_sub = self._get_user_sub_with_validation(event)

        self.user_sub_repo.update(
            obj_id=user_sub.id,
            obj_in=UserSubscriptionUpdate(
                status=SubscriptionStatus.ACTIVE,
                latest_transaction_id=event.transaction_id,
            )
        )

    @transactional
    def handle_expiration(self, event: Expiration):
        user_sub = self._get_user_sub_with_validation(event)

        self.user_sub_repo.update(
            obj_id=user_sub.id,
            obj_in=UserSubscriptionUpdate(
                status=SubscriptionStatus.EXPIRED,
                latest_transaction_id=event.transaction_id,
            )
        )

    @transactional
    def handle_transfer(self, event: Transfer):
        transfer_from_user_uuid: str = event.transferred_from[0]
        transfer_to_user_uuid: str = event.transferred_to[0]

        if transfer_from_user_uuid == transfer_to_user_uuid:
            self.logger.info(
                f"Transfer Event\n"
                f"Received same user uuid\n"
            )
            return

        # validation
        try:
            from_user: User = self.user_repo.get_by_uuid_with_subscription(user_uuid=transfer_from_user_uuid)
            to_user: User = self.user_repo.get_by_uuid_with_subscription(user_uuid=transfer_to_user_uuid)
            self.logger.error(
                f"Transfer Event validation error\n"
                f"Cannot find user matching given user uuid from event\n"
            )
        except NoResultFound:
            raise RevenuecatWebhookException()

        from_user_sub: UserSubscription = from_user.user_subscription
        to_user_sub: UserSubscription = to_user.user_subscription

        # 기존에 갖고 있던 구독 연결 해제
        self.user_sub_repo.update(
            obj_id=to_user_sub.id,
            obj_in=UserSubscriptionUpdate(
                is_current_subscription=False,
            )
        )

        # 구독 연결
        self.user_sub_repo.update(
            obj_id=from_user_sub.id,
            obj_in=UserSubscriptionUpdate(
                user_id=to_user.id,
            )
        )

        # 지갑 연결
        token_wallet: TokenWallet = self.token_domain_service.get_wallet(user_id=from_user.id)
        self.token_domain_service.change_wallet_user(token_wallet=token_wallet, user_id=to_user.id)


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
