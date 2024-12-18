from fastapi import Depends
from httplib2.auth import token
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


def get_subscription_plan_repository(db: Session = Depends(get_db)) -> SubscriptionPlanRepository:
    return SubscriptionPlanRepository(db=db)


class UserSubscriptionRepository(CRUDRepository[UserSubscription, UserSubscriptionCreate, UserSubscriptionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserSubscription, db=db)
        self.db = db

    def get_by_transaction_id(self, *, original_transaction_id: str):
        stmt = select(UserSubscription).where(UserSubscription.original_transaction_id == original_transaction_id)
        return self.db.execute(stmt).scalar_one()

    def get_by_user(self, user_id: int):
        stmt = select(UserSubscription).where(UserSubscription.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_by_user_with_plan(self, user_id: int):
        stmt = (
            select(UserSubscription)
            .where(UserSubscription.user_id == user_id)
            .options(
                joinedload(UserSubscription.subscription_plan),
            )
        )
        return self.db.execute(stmt).scalar_one()

    def get_with_user(self, original_transaction_id: str):
        stmt = (
            select(UserSubscription)
            .options(joinedload(UserSubscription.user))
            .where(UserSubscription.original_transaction_id == original_transaction_id)
        )
        return self.db.execute(stmt).scalar_one()

    def get_active_subscriptions_for_refill_with_relations(self, current_time: datetime) -> List[UserSubscription]:
        stmt = (
            select(UserSubscription)
            .join(UserSubscription.token_wallet)
            .where(
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
