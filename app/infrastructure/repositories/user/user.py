from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db.base import get_db
from app.infrastructure.repositories.crud_repository import CRUDRepository
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserCreate, UserUpdate

class UserRepository(CRUDRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=User, db=db)
        self.db = db

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email.is_(email)).first()

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db=db)