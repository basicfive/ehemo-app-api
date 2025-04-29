from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.infrastructure.repositories.crud_repository import CRUDRepository

from app.domain.training.models.user_hair_style import UserHairStyle, UserHairStyleLora
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleCreate, UserHairStyleUpdate
from app.domain.training.schemas.user_hair_style.user_hair_style_lora import UserHairStyleLoraCreate, UserHairStyleLoraUpdate

class UserHairStyleLoraRepository(CRUDRepository[UserHairStyleLora, UserHairStyleLoraCreate, UserHairStyleLoraUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserHairStyleLora, db=db)

    def get_by_request(self, training_request_id: int) -> UserHairStyleLora:
        stmt = select(UserHairStyleLora).where(UserHairStyleLora.training_request_id == training_request_id)
        return self.db.execute(stmt).scalars().one()

def get_user_hair_style_lora_repository(db: Session) -> UserHairStyleLoraRepository:
    return UserHairStyleLoraRepository(db=db)


class UserHairStyleRepository(CRUDRepository[UserHairStyle, UserHairStyleCreate, UserHairStyleUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserHairStyle, db=db)
    
    def get_with_lora(self, id: int) -> UserHairStyle:
        stmt = select(UserHairStyle).options(joinedload(UserHairStyle.user_hair_style_lora)).filter(UserHairStyle.id == id)
        return self.db.execute(stmt).scalars().one()
    
    def get_all_by_user(self, user_id: int) -> List[UserHairStyle]:
        stmt = select(UserHairStyle).filter(UserHairStyle.user_id == user_id)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

def get_user_hair_style_repository(db: Session) -> UserHairStyleRepository:
    return UserHairStyleRepository(db=db)
