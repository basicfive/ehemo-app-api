from app.domain.training.models.user_hair_style import UserHairStyle
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleUpdate
from app.domain.training.enums.user_hair_style_status import UserHairStyleStatus
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.database.transaction import transactional
from app.application.transactional_service import TransactionalService
from app.core.errors.http_exceptions import AccessUnauthorizedException
from typing import Optional

class UserHairStyleUpdateService(TransactionalService):
    def __init__(
            self,
            user_hair_style_repo: UserHairStyleRepository,
            unit_of_work: UnitOfWork,
        ):
        super().__init__(unit_of_work)
        self.user_hair_style_repo = user_hair_style_repo

    @transactional
    def soft_delete_user_hair_style(self, user_hair_style_id: int, user_id: int) -> None:
        user_hair_style: UserHairStyle = self.user_hair_style_repo.get(user_hair_style_id)
        if user_hair_style.user_id != user_id:
            raise AccessUnauthorizedException()

        self.user_hair_style_repo.update_with_flush(
            obj_id=user_hair_style_id,
            obj_in=UserHairStyleUpdate(
                status=UserHairStyleStatus.DELETED,
            )
        )

    @transactional
    def update_user_hair_style_title_and_description(
        self,
        user_id: int,
        user_hair_style_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        user_hair_style: UserHairStyle = self.user_hair_style_repo.get(user_hair_style_id)
        if user_hair_style.user_id != user_id:
            raise AccessUnauthorizedException()
        
        if not title and not description:
            return

        self.user_hair_style_repo.update_with_flush(
            obj_id=user_hair_style_id,
            obj_in=UserHairStyleUpdate(
                title=title,
                description=description,
            )
        )


from fastapi import Depends
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository
from app.infrastructure.database.unit_of_work import get_unit_of_work

def get_user_hair_style_update_service(
    user_hair_style_repo: UserHairStyleRepository = Depends(get_user_hair_style_repository),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> UserHairStyleUpdateService:
    return UserHairStyleUpdateService(
        user_hair_style_repo=user_hair_style_repo,
        unit_of_work=unit_of_work,
    )