from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from typing import List

from app.repositories.base import BaseRepository
from app.models.scene import Background, ImageResolution, PostureAndClothing
from app.schemas.scene.background import BackgroundCreate, BackgroundUpdate
from app.schemas.scene.image_resolution import ImageResolutionCreate, ImageResolutionUpdate
from app.schemas.scene.posture_and_clothing import PostureAndClothingCreate, PostureAndClothingUpdate

class BackgroundRepository(BaseRepository[Background, BackgroundCreate, BackgroundUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Background, db=db)
        self.db = db

class PostureAndClothingRepository(BaseRepository[PostureAndClothing, PostureAndClothingCreate, PostureAndClothingUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=PostureAndClothingCreate, db=db)
        self.db = db

    def get_random_records(self, limit: int = 10) -> List[PostureAndClothing]:
        stmt = select(PostureAndClothing).order_by(func.random()).limit(limit)
        return list(self.db.scalars(stmt).all())

class ImageResolutionRepository(BaseRepository[ImageResolution, ImageResolutionCreate, ImageResolutionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=ImageResolution, db=db)
        self.db = db