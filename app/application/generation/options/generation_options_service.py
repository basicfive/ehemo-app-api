from typing import List
import uuid

from app.application.generation.options.dto.generation_options import ReferenceImageUploadUrlResponse
from app.core.config import aws_s3_settings
from app.domain.generation.models.prompt import PromptComponentSuggestion, PromptComponentQuestion
from app.infrastructure.s3.s3_client import S3Client
from app.domain.training.models.user_hair_style import UserHairStyle
from app.domain.generation.models.hair_style import HairStyle
from app.domain.generation.models.image_resolution import ImageRatio
from app.infrastructure.repositories.generation.hair_style import HairStyleRepository
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository
from app.infrastructure.repositories.generation.prompt import PromptComponentQuestionRepository
from app.infrastructure.repositories.generation.image_resolution import ImageRatioRepository

from app.application.generation.options.dto.generation_options import HairStyleOption, PromptComponentOption, ImageRatioOption

class GenerationOptionsService:
    def __init__(
            self,
            hair_style_repo: HairStyleRepository,
            user_hair_style_repo: UserHairStyleRepository,
            image_ratio_repo: ImageRatioRepository,
            prompt_component_question_repo: PromptComponentQuestionRepository,
            s3_client: S3Client,
        ):
        self.hair_style_repo = hair_style_repo
        self.user_hair_style_repo = user_hair_style_repo
        self.image_ratio_repo = image_ratio_repo
        self.prompt_component_question_repo = prompt_component_question_repo
        self.s3_client = s3_client
    
    def get_reference_image_upload_url(self) -> ReferenceImageUploadUrlResponse:
        s3_key = "reference_image/" + str(uuid.uuid4())
        upload_url = self.s3_client.create_put_presigned_url(s3_key=s3_key)
        return ReferenceImageUploadUrlResponse(
            upload_url=upload_url,
            s3_key=s3_key,
        )

    def get_hair_style_options(self, user_id: int) -> List[HairStyleOption]:
        hair_style: List[HairStyle] = self.hair_style_repo.get_all()
        hair_style = sorted(hair_style, key=lambda x: x.order)

        user_hair_style: List[UserHairStyle] = self.user_hair_style_repo.get_all_by_user(user_id)
        user_hair_style = sorted(user_hair_style, key=lambda x: x.order)

        hair_style_options: List[HairStyleOption] = []
        for user_hair_style in user_hair_style:
            hair_style_options.append(
                HairStyleOption(
                    is_user_hair_style=True,
                    id=user_hair_style.id,
                    title=user_hair_style.title,
                    description=user_hair_style.description,
                    thumbnail_url=self.s3_client.create_get_presigned_url(user_hair_style.thumbnail_s3_key),
                )
            )
        
        for hair_style in hair_style:
            hair_style_options.append(
                HairStyleOption(
                    is_user_hair_style=False,
                    id=hair_style.id,
                    title=hair_style.title,
                    description=hair_style.description,
                    thumbnail_url=self.s3_client.create_get_presigned_url(hair_style.thumbnail_s3_key),
                )
            )

        return hair_style_options

    def get_prompt_component_options(self) -> List[PromptComponentOption]:
        prompt_component_questions: List[PromptComponentQuestion] = self.prompt_component_question_repo.get_all_with_suggestions()

        prompt_component_options: List[PromptComponentOption] = []
        for question in prompt_component_questions:
            suggestions: List[PromptComponentSuggestion] = question.suggestions
            suggestions = sorted(suggestions, key=lambda x: x.order)
            prompt_component_options.append(
                PromptComponentOption(
                    title=question.title,
                    question_id=question.id,
                    question=question.question,
                    suggestions=[suggestion.suggestion for suggestion in suggestions],
                )
            )

        return prompt_component_options

    def get_image_ratio_options(self) -> List[ImageRatioOption]:
        image_ratios: List[ImageRatio] = self.image_ratio_repo.get_all()
        image_ratios = sorted(image_ratios, key=lambda x: x.order)

        image_ratio_options: List[ImageRatioOption] = []
        for image_ratio in image_ratios:
            image_ratio_options.append(
                ImageRatioOption(
                    id=image_ratio.id,
                    title=image_ratio.title,
                    thumbnail_url=self.s3_client.create_get_presigned_url(image_ratio.thumbnail_s3_key),
                    description=image_ratio.description,
                    aspect_width=image_ratio.aspect_width,
                    aspect_height=image_ratio.aspect_height,
                )
            )

        return image_ratio_options
    
from fastapi import Depends
from app.infrastructure.repositories.generation.hair_style import get_hair_style_repository
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository
from app.infrastructure.repositories.generation.prompt import get_prompt_component_question_repository
from app.infrastructure.repositories.generation.image_resolution import get_image_ratio_repository
from app.infrastructure.s3.s3_client import get_s3_client
    
def get_generation_options_service(
        hair_style_repo: HairStyleRepository = Depends(get_hair_style_repository)   ,
        user_hair_style_repo: UserHairStyleRepository = Depends(get_user_hair_style_repository),
        prompt_component_question_repo: PromptComponentQuestionRepository = Depends(get_prompt_component_question_repository),
        image_ratio_repo: ImageRatioRepository = Depends(get_image_ratio_repository),
        s3_client: S3Client = Depends(get_s3_client),
) -> GenerationOptionsService:
    return GenerationOptionsService(
        hair_style_repo=hair_style_repo,
        user_hair_style_repo=user_hair_style_repo,
        prompt_component_question_repo=prompt_component_question_repo,
        image_ratio_repo=image_ratio_repo,
        s3_client=s3_client,
    )