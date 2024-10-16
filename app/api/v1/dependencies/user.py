from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.user import UserRepository
from app.services.user import UserService


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo=repo)