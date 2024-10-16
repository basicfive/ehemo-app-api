from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user.user import UserCreate, UserUpdate, UserInDB
from app.services.base import BaseService

class UserService(BaseService[User, UserInDB, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, repo: UserRepository):
        super().__init__(repo=repo, model_in_db=UserInDB)


