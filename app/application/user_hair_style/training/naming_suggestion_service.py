from typing import List

from app.infrastructure.repositories.training.suggestion import UserHairStyleTitleSuggestionRepository, UserHairStyleDescriptionSuggestionRepository
from app.application.user_hair_style.training.dto.suggestion import NamingSuggestions
from app.domain.training.models.suggestion import UserHairStyleTitleSuggestion, UserHairStyleDescriptionSuggestion
from app.infrastructure.repositories.generation.prompt import PromptComponentQuestionRepository, PromptComponentSuggestionRepository
from app.domain.generation.enums.prompt_component import PromptComponentType
from app.domain.generation.models.prompt import PromptComponentQuestion, PromptComponentSuggestion

class NamingSuggestionService:
    def __init__(
            self,
            user_hair_style_title_suggestion_repo: UserHairStyleTitleSuggestionRepository,
            user_hair_style_description_suggestion_repo: UserHairStyleDescriptionSuggestionRepository,
            prompt_component_question_repo: PromptComponentQuestionRepository,
            prompt_component_suggestion_repo: PromptComponentSuggestionRepository,
        ):
        self.user_hair_style_title_suggestion_repo = user_hair_style_title_suggestion_repo
        self.user_hair_style_description_suggestion_repo = user_hair_style_description_suggestion_repo
        self.prompt_component_question_repo = prompt_component_question_repo
        self.prompt_component_suggestion_repo = prompt_component_suggestion_repo

    def get_naming_suggestion(self) -> NamingSuggestions:
        user_hair_style_title_suggestions: List[UserHairStyleTitleSuggestion] = self.user_hair_style_title_suggestion_repo.get_all()
        user_hair_style_description_suggestions: List[UserHairStyleDescriptionSuggestion] = self.user_hair_style_description_suggestion_repo.get_all()

        length_prompt_questions: List[PromptComponentQuestion] = self.prompt_component_question_repo.get_all_by_component_type(PromptComponentType.HAIR_LENGTH)
        length_prompt_suggestions: List[PromptComponentSuggestion] = (
            self.prompt_component_suggestion_repo.get_all_by_question_ids([question.id for question in length_prompt_questions])
        )
        length_prompt_suggestions = sorted(length_prompt_suggestions, key=lambda x: x.order)

        return NamingSuggestions(
            title_suggestions=[suggestion.title for suggestion in user_hair_style_title_suggestions],
            description_suggestions=[suggestion.description for suggestion in user_hair_style_description_suggestions],
            length_prompt_suggestions=[suggestion.suggestion for suggestion in length_prompt_suggestions],
        )

from fastapi import Depends
from app.infrastructure.repositories.training.suggestion import get_user_hair_style_title_suggestion_repository, get_user_hair_style_description_suggestion_repository
from app.infrastructure.repositories.generation.prompt import get_prompt_component_question_repository, get_prompt_component_suggestion_repository

def get_naming_suggestion_service(
        user_hair_style_title_suggestion_repo: UserHairStyleTitleSuggestionRepository = Depends(get_user_hair_style_title_suggestion_repository),
        user_hair_style_description_suggestion_repo: UserHairStyleDescriptionSuggestionRepository = Depends(get_user_hair_style_description_suggestion_repository),
        prompt_component_question_repo: PromptComponentQuestionRepository = Depends(get_prompt_component_question_repository),
        prompt_component_suggestion_repo: PromptComponentSuggestionRepository = Depends(get_prompt_component_suggestion_repository),
) -> NamingSuggestionService:
    return NamingSuggestionService(
        user_hair_style_title_suggestion_repo=user_hair_style_title_suggestion_repo,
        user_hair_style_description_suggestion_repo=user_hair_style_description_suggestion_repo,
        prompt_component_question_repo=prompt_component_question_repo,
        prompt_component_suggestion_repo=prompt_component_suggestion_repo,
    )