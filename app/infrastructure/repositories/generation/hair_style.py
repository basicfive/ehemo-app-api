from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.db.base import get_db
from app.domain.generation.models.hair_style import HairStyle, HairStyleLora
from app.domain.generation.schemas.hair_style.hair_style import HairStyleCreate, HairStyleUpdate
from app.domain.generation.schemas.hair_style.hair_style_lora import HairStyleLoraCreate, HairStyleLoraUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository

class HairStyleLoraRepository(CRUDRepository[HairStyleLora, HairStyleLoraCreate, HairStyleLoraUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairStyleLora, db=db)
    
def get_hair_style_lora_repository(db: Session = Depends(get_db)) -> HairStyleLoraRepository:
    return HairStyleLoraRepository(db=db)

class HairStyleRepository(CRUDRepository[HairStyle, HairStyleCreate, HairStyleUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=HairStyle, db=db)
    
    def get_with_lora(self, id: int) -> HairStyle:
        stmt = select(HairStyle).options(joinedload(HairStyle.hair_style_lora)).filter(HairStyle.id == id)
        return self.db.execute(stmt).scalars().one()
    
def get_hair_style_repository(db: Session = Depends(get_db)) -> HairStyleRepository:
    return HairStyleRepository(db=db)

