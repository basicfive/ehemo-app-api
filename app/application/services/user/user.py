from app.infrastructure.repositories.user.user import UserRepository


class UserApplicationService:
    def __init__(
            self,
            user_repo: UserRepository
    ):
        self.user_repo = user_repo

    # def