from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, user_create: UserCreate):
        self.user_repo.create(obj_in=user_create)

    def update_user(self, user_id: int, user_update: UserUpdate):
        self.user_repo.update(obj_id=user_id, obj_in=user_update)

