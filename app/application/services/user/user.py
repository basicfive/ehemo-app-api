from fastapi import Depends

from app.application.services.transactional_service import TransactionalService
from app.application.services.user.dto.user_info import UserInfoResponse, UserTokenResponse
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserUpdate
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class UserApplicationService(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo

    def get_user_token(self, user_id: int) -> UserTokenResponse:
        user_with_subscription: User = self.user_repo.get_with_subscription(user_id=user_id)
        return UserTokenResponse(token=user_with_subscription.subscription.remaining_token)

    def get_user_info(self, user_id: int) -> UserInfoResponse:
        user_with_subscription: User = self.user_repo.get_with_subscription(user_id=user_id)
        return UserInfoResponse(
            uuid=str(user_with_subscription.uuid),
            email=user_with_subscription.email,
            token=user_with_subscription.subscription.remaining_token,
        )

    @transactional
    def soft_delete_user(self, user_id: int):
        self.user_repo.update(obj_id=user_id, obj_in=UserUpdate(deleted=True))

    @transactional
    def update_fcm_token(self, fcm_token: str, user_id: int) -> UserInfoResponse:
        user_with_subscription: User = self.user_repo.get_with_subscription(user_id=user_id)

        if user_with_subscription.fcm_token != fcm_token:
            self.user_repo.update(obj_id=user_with_subscription.id, obj_in=UserUpdate(fcm_token=fcm_token))

        return UserInfoResponse(
            uuid=str(user_with_subscription.uuid),
            email=user_with_subscription.email,
            token=user_with_subscription.subscription.remaining_token,
        )

def get_user_application_service(
        user_repo: UserRepository = Depends(get_user_repository),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):
    return UserApplicationService(
        user_repo=user_repo,
        unit_of_work=unit_of_work,
    )
