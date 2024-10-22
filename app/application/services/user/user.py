from app.domain.user.models.user import User
from app.infrastructure.repositories.user.user import UserRepository
from app.domain.user.schemas.user import UserCreate, UserUpdate, UserInDB
from app.application.services.base_service import CRUDService

class UserApplicationService:
    def __init__(
            self,
            user_repo: UserRepository
    ):
        self.user_repo = user_repo




