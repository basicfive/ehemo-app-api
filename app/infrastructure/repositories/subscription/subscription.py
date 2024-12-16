from typing import List
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.core.db.base import get_db
from app.domain.subscription.models.enums.subscription import SubscriptionStatus, SubscriptionPlanType
from app.domain.subscription.models.subscription import Subscription
from app.domain.subscription.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository


class SubscriptionRepository(CRUDRepository[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Subscription, db=db)
        self.db = db

    def get_by_transaction_id(self, *, original_transaction_id: str):
        stmt = select(Subscription).where(Subscription.original_transaction_id == original_transaction_id)
        return self.db.execute(stmt).scalar_one()

    def get_by_user(self, user_id: int):
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_with_user(self, original_transaction_id: str):
        stmt = (
            select(Subscription)
            .options(joinedload(Subscription.user))
            .where(Subscription.original_transaction_id == original_transaction_id)
        )
        return self.db.execute(stmt).scalar_one()

    def get_subscriptions_for_token_refresh(self, current_time: datetime) -> List[Subscription]:
        stmt = select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.plan_type != SubscriptionPlanType.FREE,
            Subscription.next_token_refill_date <= current_time
        )
        return list(self.db.scalars(stmt).all())

def get_subscription_repository(db: Session = Depends(get_db)):
    return SubscriptionRepository(db=db)