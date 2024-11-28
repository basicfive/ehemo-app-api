from fastapi import Depends


from app.application.services.user.dto.user_info import UserInfoResponse, UserTokenResponse
from app.domain.user.models.user import User
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class UserInfoApplicationService:
    def __init__(
            self,
            user_repo: UserRepository
    ):
        self.user_repo = user_repo

    def get_user_token(self, user_id: int) -> UserTokenResponse:
        user: User = self.user_repo.get(obj_id=user_id)
        return UserTokenResponse(token=user.token)

    def get_user_info(self, user_id: int) -> UserInfoResponse:
        user: User = self.user_repo.get(obj_id=user_id)
        return UserInfoResponse(
            uuid=str(user.uuid),
            email=user.email,
            token=user.token,
        )

def get_user_info_application_service(
        user_repo: UserRepository = Depends(get_user_repository)
):
    return UserInfoApplicationService(user_repo=user_repo)
