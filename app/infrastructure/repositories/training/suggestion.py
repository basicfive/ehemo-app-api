from sqlalchemy.orm import Session
from app.infrastructure.repositories.crud_repository import CRUDRepository

from app.domain.training.models.suggestion import UserHairStyleTitleSuggestion, UserHairStyleDescriptionSuggestion
from app.domain.training.schemas.suggestion.user_hair_style_title_suggestion import UserHairStyleTitleSuggestionCreate, UserHairStyleTitleSuggestionUpdate, UserHairStyleTitleSuggestionInDB
from app.domain.training.schemas.suggestion.user_hair_style_description_suggestion import UserHairStyleDescriptionSuggestionCreate, UserHairStyleDescriptionSuggestionUpdate, UserHairStyleDescriptionSuggestionInDB
from fastapi import Depends
from app.core.db.base import get_db

class UserHairStyleTitleSuggestionRepository(CRUDRepository[UserHairStyleTitleSuggestion, UserHairStyleTitleSuggestionCreate, UserHairStyleTitleSuggestionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserHairStyleTitleSuggestion, db=db)

def get_user_hair_style_title_suggestion_repository(db: Session = Depends(get_db)) -> UserHairStyleTitleSuggestionRepository:
    return UserHairStyleTitleSuggestionRepository(db=db)


class UserHairStyleDescriptionSuggestionRepository(CRUDRepository[UserHairStyleDescriptionSuggestion, UserHairStyleDescriptionSuggestionCreate, UserHairStyleDescriptionSuggestionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserHairStyleDescriptionSuggestion, db=db)

def get_user_hair_style_description_suggestion_repository(db: Session = Depends(get_db)) -> UserHairStyleDescriptionSuggestionRepository:
    return UserHairStyleDescriptionSuggestionRepository(db=db)