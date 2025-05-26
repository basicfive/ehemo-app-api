from typing import Tuple
from uuid import uuid4

from app.domain.common.enums.gender import Gender
from app.core.config import aws_s3_settings
from app.infrastructure.repositories.generation.prompt import ClothingPromptExampleRepository, PosePromptExampleRepository

def get_thumbnail_image_size() -> Tuple[int, int]:
    width = 896
    height = 1152
    return width, height

def create_user_hair_style_thumbnail_s3_key() -> str:
    return aws_s3_settings.USER_HAIR_STYLE_THUMBNAIL_S3KEY_PREFIX + str(uuid4())

class ThumbnailPromptService:
    def __init__(
            self,
            clothing_prompt_example_repo: ClothingPromptExampleRepository,
            pose_prompt_example_repo: PosePromptExampleRepository,
    ):
        self.clothing_prompt_example_repo = clothing_prompt_example_repo
        self.pose_prompt_example_repo = pose_prompt_example_repo

    def create_thumbnail_prompt(self, gender: Gender, length_prompt: str) -> str:
        clothing_prompt_example = self.clothing_prompt_example_repo.get_random_by_gender(gender)
        pose_prompt_example = self.pose_prompt_example_repo.get_random()

        gender_prompt = "남성" if gender == Gender.MALE else "여성"

        return (
            f"25세 한국인 {gender_prompt}의 사진, "
            f"{length_prompt}, (ohwx hair:1.4), {clothing_prompt_example.prompt}, {pose_prompt_example.prompt}, "
            f"흰색 벽 앞에 서 있음"
        )

from fastapi import Depends
from app.infrastructure.repositories.generation.prompt import get_clothing_prompt_example_repository, get_pose_prompt_example_repository

def get_thumbnail_prompt_service(
        clothing_prompt_example_repo: ClothingPromptExampleRepository = Depends(get_clothing_prompt_example_repository),
        pose_prompt_example_repo: PosePromptExampleRepository = Depends(get_pose_prompt_example_repository),
) -> ThumbnailPromptService:
    return ThumbnailPromptService(
        clothing_prompt_example_repo=clothing_prompt_example_repo,
        pose_prompt_example_repo=pose_prompt_example_repo,
    )