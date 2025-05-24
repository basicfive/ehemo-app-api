from typing import List

from app.infrastructure.repositories.training.suggestion import UserHairStyleTitleSuggestionRepository, UserHairStyleDescriptionSuggestionRepository
from app.application.user_hair_style.training.dto.suggestion import NamingSuggestions
from app.domain.training.models.suggestion import UserHairStyleTitleSuggestion, UserHairStyleDescriptionSuggestion

class NamingSuggestionService:
    def __init__(
            self,
            user_hair_style_title_suggestion_repo: UserHairStyleTitleSuggestionRepository,
            user_hair_style_description_suggestion_repo: UserHairStyleDescriptionSuggestionRepository,
        ):
        self.user_hair_style_title_suggestion_repo = user_hair_style_title_suggestion_repo
        self.user_hair_style_description_suggestion_repo = user_hair_style_description_suggestion_repo

    def get_naming_suggestion(self) -> NamingSuggestions:
        user_hair_style_title_suggestions: List[UserHairStyleTitleSuggestion] = self.user_hair_style_title_suggestion_repo.get_all()
        user_hair_style_description_suggestions: List[UserHairStyleDescriptionSuggestion] = self.user_hair_style_description_suggestion_repo.get_all()

        return NamingSuggestions(
            title_suggestions=[suggestion.title for suggestion in user_hair_style_title_suggestions],
            description_suggestions=[suggestion.description for suggestion in user_hair_style_description_suggestions],
        )

from fastapi import Depends
from app.infrastructure.repositories.training.suggestion import get_user_hair_style_title_suggestion_repository, get_user_hair_style_description_suggestion_repository

def get_naming_suggestion_service(
        user_hair_style_title_suggestion_repo: UserHairStyleTitleSuggestionRepository = Depends(get_user_hair_style_title_suggestion_repository),
        user_hair_style_description_suggestion_repo: UserHairStyleDescriptionSuggestionRepository = Depends(get_user_hair_style_description_suggestion_repository),
) -> NamingSuggestionService:
    return NamingSuggestionService(
        user_hair_style_title_suggestion_repo=user_hair_style_title_suggestion_repo,
        user_hair_style_description_suggestion_repo=user_hair_style_description_suggestion_repo,
    )