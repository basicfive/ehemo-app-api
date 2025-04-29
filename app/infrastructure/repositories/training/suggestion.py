from sqlalchemy.orm import Session
from app.infrastructure.repositories.crud_repository import CRUDRepository

from app.domain.training.models.suggestion import UserHairStyleTitleSuggestion, UserHairStyleDescriptionSuggestion
from app.domain.training.schemas.suggestion.user_hair_style_title_suggestion import UserHairStyleTitleSuggestionCreate, UserHairStyleTitleSuggestionUpdate, UserHairStyleTitleSuggestionInDB
from app.domain.training.schemas.suggestion.user_hair_style_description_suggestion import UserHairStyleDescriptionSuggestionCreate, UserHairStyleDescriptionSuggestionUpdate, UserHairStyleDescriptionSuggestionInDB

class UserHairStyleSuggestionRepository(CRUDRepository[UserHairStyleTitleSuggestion, UserHairStyleTitleSuggestionCreate, UserHairStyleTitleSuggestionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserHairStyleTitleSuggestion, db=db)

def get_user_hair_style_title_suggestion_repository(db: Session) -> UserHairStyleSuggestionRepository:
    return UserHairStyleSuggestionRepository(db=db)


class UserHairStyleDescriptionSuggestionRepository(CRUDRepository[UserHairStyleDescriptionSuggestion, UserHairStyleDescriptionSuggestionCreate, UserHairStyleDescriptionSuggestionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=UserHairStyleDescriptionSuggestion, db=db)

def get_user_hair_style_description_suggestion_repository(db: Session) -> UserHairStyleDescriptionSuggestionRepository:
    return UserHairStyleDescriptionSuggestionRepository(db=db)