from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import List

from app.core.db.base import get_db
from app.domain.subscription.models.enums.subscription import SubscriptionStatus, SubscriptionPlanType, StoreType
from app.domain.subscription.schemas.subscription_plan import SubscriptionPlanUpdate, SubscriptionPlanCreate
from app.domain.token.models.token import TokenWallet
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.subscription.models.subscription import UserSubscription, SubscriptionPlan
from app.domain.subscription.schemas.user_subscription import UserSubscriptionCreate, UserSubscriptionUpdate

class SubscriptionPlanRepository(CRUDRepository[SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=SubscriptionPlan)

    def get_all_by_store_type(self, store_type: StoreType) -> List[SubscriptionPlan]:
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.store_type == store_type)
        return list(self.db.scalars(stmt).all())

    def get_by_product_id(self, product_id: str) -> SubscriptionPlan:
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.product_id == product_id)
        return self.db.execute(stmt).scalar_one()

def get_subscription_plan_repository(db: Session = Depends(get_db)) -> SubscriptionPlanRepository:
    return SubscriptionPlanRepository(db=db)


class UserSubscriptionRepository(CRUDRepository[UserSubscription, UserSubscriptionCreate, UserSubscriptionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserSubscription, db=db)
        self.db = db

    def get_current_by_og_transaction_id(self, original_transaction_id: str):
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.original_transaction_id == original_transaction_id,
                UserSubscription.is_current == True,
            )
        )
        return self.db.execute(stmt).scalar_one()

    def get_latest_by_product_id(self, user_id: int, product_id: str):
        stmt = (
            select(UserSubscription)
            .join(UserSubscription.subscription_plan)
            .where(
                UserSubscription.user_id == user_id,
                SubscriptionPlan.product_id == product_id,
            )
            .order_by(UserSubscription.purchase_date.desc())  # 가장 최근 구매 순으로 정렬
            .limit(1)  # 최상위 1개만 가져오기
        )
        return self.db.execute(stmt).scalar_one()

    def get_current_by_og_t_id_w_wallet(self, original_transaction_id: str):
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.original_transaction_id == original_transaction_id,
                UserSubscription.is_current == True,
            )
            .options(joinedload(UserSubscription.token_wallet))
        )
        return self.db.execute(stmt).unique().scalar_one()

    def get_current_by_og_t_id_w_relations(self, original_transaction_id: str):
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.original_transaction_id == original_transaction_id,
                UserSubscription.is_current == True,
            )
            .options(
                joinedload(UserSubscription.subscription_plan),
                joinedload(UserSubscription.token_wallet),
                joinedload(UserSubscription.user),
            )
        )
        return self.db.execute(stmt).unique().scalar_one()

    def get_current_by_user_with_wallet(self, user_id: int):
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.is_current == True,
            )
            .options(joinedload(UserSubscription.token_wallet))
        )
        return self.db.execute(stmt).scalar_one()

    def get_current_by_user(self, user_id: int):
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.is_current == True,
            )
        )
        return self.db.execute(stmt).scalar_one()

    def get_current_by_user_with_plan(self, user_id: int):
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.is_current == True,
            )
            .options(
                joinedload(UserSubscription.subscription_plan),
            )
        )
        return self.db.execute(stmt).unique().scalar_one()

    def get_all_by_user_with_plan(self, user_id: int) -> List[UserSubscription]:
        stmt = (
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
            )
            .options(
                joinedload(UserSubscription.subscription_plan),
            )
        )
        return list(self.db.scalars(stmt).all())

    def get_active_subscriptions_for_refill_with_relations(self, current_time: datetime) -> List[UserSubscription]:
        stmt = (
            select(UserSubscription)
            .join(UserSubscription.token_wallet)
            .where(
                UserSubscription.is_current == True,
                UserSubscription.status == SubscriptionStatus.ACTIVE,
                TokenWallet.next_refill_date <= current_time
            )
            .options(
                joinedload(UserSubscription.token_wallet),
                joinedload(UserSubscription.user),
                joinedload(UserSubscription.subscription_plan)
            )
        )
        return list(self.db.scalars(stmt).all())

def get_user_subscription_repository(db: Session = Depends(get_db)):
    return UserSubscriptionRepository(db=db)
