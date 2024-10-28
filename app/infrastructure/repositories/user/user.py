from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserCreate, UserUpdate

class UserRepository(CRUDRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=User, db=db)
        self.db = db

    def get_by_social_account(self, provider: str, social_id: str) -> User:
        stmt = select(User).filter_by(provider=provider, social_id=social_id)
        return self.db.execute(stmt).scalar_one()

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db=db)