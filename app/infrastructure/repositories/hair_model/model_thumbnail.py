from typing import List

from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.db.base import get_db
from app.domain.hair_model.models.model_thumbnail import ModelThumbnail
from app.domain.hair_model.schemas.button_thumbnail.button_thumbnail import ModelThumbnailCreate, ModelThumbnailUpdate
from app.infrastructure.repositories.crud_repository import CRUDRepository


class ModelThumbnailRepository(CRUDRepository[ModelThumbnail, ModelThumbnailCreate, ModelThumbnailUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ModelThumbnail, db=db)
        self.db = db

    def get_all_in_order(self):
        model_thumbnail_list: List[ModelThumbnail] = self.get_all()
        return sorted(model_thumbnail_list, key=lambda x: x.order)

def get_model_thumbnail_repository(db: Session = Depends(get_db)) -> ModelThumbnailRepository:
    return ModelThumbnailRepository(db=db)

