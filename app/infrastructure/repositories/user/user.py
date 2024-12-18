from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from datetime import datetime

from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserCreate, UserUpdate

class UserRepository(CRUDRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=User, db=db)
        self.db = db

    def get_by_social_account(self, provider: str, social_id: str) -> User:
        stmt = select(User).filter_by(provider=provider, social_id=social_id, deleted=False)
        return self.db.execute(stmt).scalar_one()

    def get_with_subscription(self, user_id: int):
        stmt = select(User).options(joinedload(User.subscription)).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_with_token_wallet(self, user_id: int):
        stmt = select(User).options(joinedload(User.token_wallet)).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        stmt = select(User).where(User.id.in_(user_ids))
        return list(self.db.scalars(stmt).all())

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db=db)