from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserCreate, UserUpdate

class UserRepository(CRUDRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=User, db=db)
        self.db = db

    def get_active_by_social_account(self, provider: str, social_id: str) -> User:
        stmt = select(User).filter_by(provider=provider, social_id=social_id, deleted=False)
        return self.db.execute(stmt).scalar_one()

    def get_all_by_social_id_with_user_subs(self, social_id: str) -> List[User]:
        stmt = (
            select(User)
            .options(joinedload(User.user_subscriptions))
            .where(User.social_id == social_id)
        )
        return list(self.db.scalars(stmt).unique().all())

    def get_with_subscriptions(self, user_id: int) -> User:
        stmt = (
            select(User)
            .options(joinedload(User.user_subscriptions))
            .where(User.id == user_id)
        )
        return self.db.execute(stmt).unique().scalar_one()

    def get_by_uuid_with_subscriptions(self, user_uuid: str) -> User:
        stmt = (
            select(User)
            .options(joinedload(User.user_subscriptions))
            .where(User.uuid == user_uuid)
        )
        return self.db.execute(stmt).unique().scalar_one()

    def get_with_token_wallets(self, user_id: int) -> User:
        stmt = (
            select(User)
            .options(joinedload(User.token_wallets))
            .where(User.id == user_id)
        )
        return self.db.execute(stmt).unique().scalar_one()

    def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        stmt = select(User).where(User.id.in_(user_ids))
        return list(self.db.scalars(stmt).all())

    def get_by_uuid(self, user_uuid: str):
        stmt = select(User).where(User.uuid == user_uuid)
        return self.db.execute(stmt).scalar_one()

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db=db)