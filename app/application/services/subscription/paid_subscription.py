from fastapi import Depends
from datetime import datetime
import logging

from sqlalchemy.exc import NoResultFound

from app.application.services.subscription.dto.revenue_cat.event import *
from app.application.services.transactional_service import TransactionalService
from app.core.errors.http_exceptions import RevenuecatWebhookException
from app.core.utils import ms_to_datetime, extract_valid_uuid
from app.domain import User, SubscriptionPlan, SubscriptionStatus, UserSubscription, TokenWallet, TokenSourceType, \
    SubscriptionPlanType
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

    def _get_user_sub_with_validation(self, event: BaseEvent) -> UserSubscription:
        try:
            user_sub: UserSubscription = (
                self.user_sub_repo.get_current_by_og_transaction_id(event.original_transaction_id)
            )
        except NoResultFound:
            self.logger.error(
                f"There is no current user subscription with original_transaction_id: {event.original_transaction_id}"
            )
            raise RevenuecatWebhookException()
        return user_sub

    def _get_latest_user_sub_by_product_id(self, event: BaseEvent) -> UserSubscription:
        try:
            user: User = self.user_repo.get_by_uuid(user_uuid=event.app_user_id)
            user_sub: UserSubscription = (
                self.user_sub_repo.get_latest_by_product_id(user.id, event.product_id)
            )
        except NoResultFound:
            self.logger.error(
                f"There is no latest user subscription with product_id: {event.product_id}"
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
                is_current=True,
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
        try:
            user: User = self.user_repo.get_by_uuid(event.app_user_id)
        except NoResultFound:
            self.logger.error(
                f"Initial Purchase Event error\n"
                f"Cannot find matching user given user uuid from event\n"
            )
            raise RevenuecatWebhookException()

        # 존재하는 구독에 대해 현재 연결된 구독이 아닌 상태로 변경
        try:
            paid_user_sub: UserSubscription = (
                self.user_sub_repo.get_current_by_og_t_id_w_wallet(event.original_transaction_id)
            )
            self.user_sub_repo.update_with_flush(
                obj_id=paid_user_sub.id,
                obj_in=UserSubscriptionUpdate(is_current=False, status=SubscriptionStatus.CHANGED)
            )
            self.token_domain_service.disable_wallet(token_wallet=paid_user_sub.token_wallet)
        except NoResultFound:
            pass
        try:
            free_user_sub: UserSubscription = (
                self.user_sub_repo.get_current_by_user_with_wallet(user.id)
            )
            self.user_sub_repo.update_with_flush(
                obj_id=free_user_sub.id,
                obj_in=UserSubscriptionUpdate(is_current=False, status=SubscriptionStatus.CHANGED)
            )
            self.token_domain_service.disable_wallet(token_wallet=free_user_sub.token_wallet)
        except NoResultFound:
            pass

        self._create_new_subscription_for_user(user=user, event=event)

    def _initial_purchase_but_renew(self, event: Renewal):
        """
        해당 (스토어)계정으로 구매한 적은 없으나, 애플 등 스토어 계정에 연동된 구매한 이력이 남아있어,
        TRANSFER / RENEW 로 요청이 오는 경우 우선 구매 처리를 정상적으로 하기 위해서 구현함.
        """
        self.logger.info(
            f"RENEWAL: There is no current user sub with original_transaction_id of : {event.original_transaction_id}\n"
            f"Creating new user subscription for user (user_uuid): {event.app_user_id}"
        )
        try:
            user: User = self.user_repo.get_by_uuid(event.app_user_id)
        except NoResultFound:
            self.logger.error(f"There is no user with user_uuid: {event.app_user_id}")
            return
        try:
            # 이전에 구독하던 것이 있는 경우
            existing_user_sub: UserSubscription = self.user_sub_repo.get_current_by_user(user.id)
            self.user_sub_repo.update_with_flush(
                obj_id=existing_user_sub.id,
                obj_in=UserSubscriptionUpdate(
                    is_current=False,
                )
            )
        except NoResultFound:
            pass
        self._create_new_subscription_for_user(user=user, event=event)


    @transactional
    def handle_renewal(self, event: Renewal):
        """구독 갱신 이벤트 처리"""
        try:
            user_sub_with_relations = self.user_sub_repo.get_current_by_og_t_id_w_relations(event.original_transaction_id)
        except NoResultFound:
            # 스토어 계정 연동으로 인해 해당 계정으로는 구매한 적이 없어 INITIAL PURCHASE 로 예상되었던 값이 RENEW로 오는 경우
            self._initial_purchase_but_renew(event)
            return

        subscription_plan: SubscriptionPlan = user_sub_with_relations.subscription_plan
        token_wallet: TokenWallet = user_sub_with_relations.token_wallet
        user: User = user_sub_with_relations.user
        purchase_date: datetime = ms_to_datetime(event.purchased_at_ms)

        # 새로운 plan 을 생성
        if subscription_plan.product_id != event.product_id:
            # PRODUCT CHANGE 하고 RENEW 로 이벤트 오는 경우
            self._handle_product_change(user_sub_with_relations=user_sub_with_relations, event=event)
            return
        if user_sub_with_relations.status == SubscriptionStatus.EXPIRED:
            # EXPIRED -> RENEW 로 다시 구매한 유저에 대한 처리
            self._handle_resubscription(user_sub_with_relations=user_sub_with_relations, event=event)
            return

        # if user_sub_with_relations.status != SubscriptionStatus.ACTIVE:
        #     return

        # 기존 plan 업데이트 (renew)
        self.user_sub_repo.update(
            obj_id=user_sub_with_relations.id,
            obj_in=UserSubscriptionUpdate(
                latest_transaction_id=event.transaction_id,
                purchase_date=purchase_date,
                expire_date=ms_to_datetime(event.expiration_at_ms),
                status=SubscriptionStatus.ACTIVE, # canceled 등의 경우 고려
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
        token_wallet: TokenWallet = user_sub_with_relations.token_wallet

        self.user_sub_repo.update(
            obj_id=user_sub_with_relations.id,
            obj_in=UserSubscriptionUpdate(
                is_current=False,
                status=SubscriptionStatus.CHANGED
            )
        )
        self.token_domain_service.disable_wallet(token_wallet=token_wallet)

        self._create_new_subscription_for_user(user=user, event=event)

    def _handle_resubscription(
            self,
            user_sub_with_relations: UserSubscription,
            event: Renewal
    ):
        """EXPIRED -> RENEW 로 다시 구매한 유저에 대한 처리"""
        user: User = user_sub_with_relations.user
        token_wallet: TokenWallet = user_sub_with_relations.token_wallet

        self.user_sub_repo.update(
            obj_id=user_sub_with_relations.id,
            obj_in=UserSubscriptionUpdate(
                is_current=False,
            )
        )
        self.token_domain_service.disable_wallet(token_wallet=token_wallet)

        self._create_new_subscription_for_user(user=user, event=event)


    @transactional
    def handle_cancellation(self, event: Cancellation):
        """구독 취소 이벤트 처리"""
        user_sub = self._get_latest_user_sub_by_product_id(event)

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
        transfer_from_user_uuid: str = extract_valid_uuid(event.transferred_from)
        transfer_to_user_uuid: str = extract_valid_uuid(event.transferred_to)

        if transfer_from_user_uuid == transfer_to_user_uuid:
            self.logger.info(
                f"Transfer Event\n"
                f"Received same user uuid\n"
            )
            return

        # validation
        try:
            from_user: User = self.user_repo.get_by_uuid_with_subscriptions(user_uuid=transfer_from_user_uuid)
            to_user: User = self.user_repo.get_by_uuid_with_subscriptions(user_uuid=transfer_to_user_uuid)
        except NoResultFound:
            self.logger.error(
                f"Transfer Event validation error\n"
                f"Cannot find matching user given user uuid from event\n"
            )
            raise RevenuecatWebhookException()

        from_user_sub: UserSubscription = from_user.current_subscription
        to_user_sub: UserSubscription = to_user.current_subscription

        # 기존에 갖고 있던 구독 연결 해제 (있다면)
        if to_user_sub:
            self.user_sub_repo.update_with_flush(
                obj_id=to_user_sub.id,
                obj_in=UserSubscriptionUpdate(
                    is_current=False,
                    status=SubscriptionStatus.TRANSFERRED
                )
            )
            to_user_wallet: TokenWallet = self.token_domain_service.get_wallet(user_id=to_user.id)
            self.token_domain_service.disable_wallet(token_wallet=to_user_wallet)

        # 구독 연결
        self.user_sub_repo.update(
            obj_id=from_user_sub.id,
            obj_in=UserSubscriptionUpdate(
                user_id=to_user.id,
            )
        )

        # 지갑 연결
        from_user_wallet: TokenWallet = self.token_domain_service.get_wallet(user_id=from_user.id)
        self.token_domain_service.change_wallet_user(token_wallet=from_user_wallet, user_id=to_user.id)


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
