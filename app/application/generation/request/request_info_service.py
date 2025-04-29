import logging
from fastapi.params import Depends
from typing import List, Optional
from datetime import datetime, timedelta

from app.domain.generation.schemas.hair_style.hair_style import HairStyleInDB
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleInDB
from app.domain.generation.models.image_resolution import ImageRatio
from app.domain.generation.schemas.image_resolution.image_ratio import ImageRatioInDB
from app.infrastructure.repositories.generation.image_resolution import ImageRatioRepository
from app.domain.generation.models.hair_style import HairStyle
from app.domain.generation.models.image_resolution import ImageResolution
from app.domain.training.models.user_hair_style import UserHairStyle
from app.domain.generation.enums.prompt_component import PromptComponentType
from app.domain.generation.dto.request_generation import PromptComponentAnswer
from app.application.generation.options.dto.generation_options import HairStyleOption, PromptComponentOption, ImageRatioOption
from app.domain.generation.schemas.generation.generation_request import GenerationRequestInDB
from app.application.generation.request.dto.request_info import GenerationRequestInfo
from app.application.transactional_service import TransactionalService
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, GenerationJobRepository
from app.domain.generation.models.generation import GenerationRequest, GenerationJob
from app.domain.generation.models.generation import RequestPromptComponentQuestionAnswer
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository
from app.core.errors.http_exceptions import AccessUnauthorizedException
from app.infrastructure.repositories.generation.generation import RequestPromptComponentQuestionAnswerRepository
from app.infrastructure.s3.s3_client import S3Client

class GenerationRequestInfoService(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            generation_request_repo: GenerationRequestRepository,
            image_ratio_repo: ImageRatioRepository,
            generation_job_repo: GenerationJobRepository,
            request_prompt_component_question_answer_repo: RequestPromptComponentQuestionAnswerRepository,
            s3_client: S3Client,
    ):
        self.user_repo = user_repo
        self.generation_request_repo = generation_request_repo
        self.generation_job_repo = generation_job_repo
        self.image_ratio_repo = image_ratio_repo
        self.request_prompt_component_question_answer_repo = request_prompt_component_question_answer_repo
        self.s3_client = s3_client

    def get_generation_request_status(self, generation_request_id: int, user_id: int):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise AccessUnauthorizedException()

    def get_generated_request_info(self, generation_request_id: int, user_id: int) -> GenerationRequestInfo:
        
        # validation
        generation_request_w_relations: GenerationRequest = self.generation_request_repo.get_with_relations(generation_request_id)
        if generation_request_w_relations.user_id != user_id:
            raise AccessUnauthorizedException()

        # 남은 시간 계산
        generation_job: GenerationJob = self.generation_job_repo.get_by_generation_request(generation_request_w_relations.id)
        time_delta: timedelta = generation_job.expires_at - datetime.now()
        remaining_sec: int = time_delta.total_seconds()

        # 헤어스타일 옵션 가져오기
        if generation_request_w_relations.is_user_hair_style:
            user_hair_style: UserHairStyle = generation_request_w_relations.user_hair_style
            user_hair_style_indb: UserHairStyleInDB = UserHairStyleInDB.model_validate(user_hair_style)
            selected_hair_style_option = HairStyleOption(
                is_user_hair_style=True,
                **user_hair_style_indb.model_dump(),
                thumbnail_url=self.s3_client.get_thumbnail_url(user_hair_style.thumbnail_s3_key),
            )
        else:
            hair_style: HairStyle = generation_request_w_relations.hair_style
            hair_style_indb: HairStyleInDB = HairStyleInDB.model_validate(hair_style)
            selected_hair_style_option = HairStyleOption(
                is_user_hair_style=False,
                **hair_style_indb.model_dump(),
                thumbnail_url=self.s3_client.get_thumbnail_url(hair_style.thumbnail_s3_key),
            )


        # 프롬프트 컴포넌트 답변 가져오기
        request_prompt_component_question_answers: List[RequestPromptComponentQuestionAnswer] = (
            self.request_prompt_component_question_answer_repo.get_all_by_generation_request_with_question(generation_request_id)
        )

        selected_prompt_component_answer: List[PromptComponentAnswer] = []
        for request_prompt_component_question_answer in request_prompt_component_question_answers:
            selected_prompt_component_answer.append(
                PromptComponentAnswer(
                    prompt_component_question_id=request_prompt_component_question_answer.prompt_component_question_id,
                    # 서버에서는 해당 값을 저장하지 않고, 프론트에서 answer를 기준으로 random 여부를 결정해서 보내므로 인위적인 False 값을 넣음.
                    is_random=False,
                    answer=request_prompt_component_question_answer.answer,
                )
            )

        # 이미지 비율 옵션 가져오기
        image_resolution: ImageResolution = generation_request_w_relations.image_resolution
        image_ratio: ImageRatio = self.image_ratio_repo.get(image_resolution.image_ratio_id)
        image_ratio_indb = ImageRatioInDB.model_validate(image_ratio)

        selected_image_ratio_option = ImageRatioOption(
            **image_ratio_indb.model_dump(),
            thumbnail_url=self.s3_client.get_thumbnail_url(image_ratio.thumbnail_s3_key),
        )

        generation_request_indb: GenerationRequestInDB = GenerationRequestInDB.model_validate(generation_request_w_relations)

        return GenerationRequestInfo(
            **generation_request_indb.model_dump(),
            generation_request_id=generation_request_w_relations.id,
            remaining_sec=remaining_sec,
            user_reference_image_thumbnail_url=self.s3_client.get_thumbnail_url(generation_request_w_relations.user_reference_image_s3_key),
            selected_hair_style_option=selected_hair_style_option,
            selected_prompt_component_answer=selected_prompt_component_answer,
            selected_image_ratio_option=selected_image_ratio_option,
        )


from fastapi import Depends

from app.infrastructure.repositories.generation.generation import get_generation_request_repository, get_generation_job_repository, \
    get_request_prompt_component_question_answer_repository
from app.infrastructure.s3.s3_client import get_s3_client
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.repositories.generation.image_resolution import get_image_ratio_repository

def get_generation_request_info_service(
    user_repo: UserRepository = Depends(get_user_repository),
    generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
    image_ratio_repo: ImageRatioRepository = Depends(get_image_ratio_repository),
    generation_job_repo: GenerationJobRepository = Depends(get_generation_job_repository),
    request_prompt_component_question_answer_repo: RequestPromptComponentQuestionAnswerRepository = Depends(get_request_prompt_component_question_answer_repository),
    s3_client: S3Client = Depends(get_s3_client),
) -> GenerationRequestInfoService:
    return GenerationRequestInfoService(
        user_repo=user_repo,
        generation_request_repo=generation_request_repo,
        image_ratio_repo=image_ratio_repo,
        generation_job_repo=generation_job_repo,
        request_prompt_component_question_answer_repo=request_prompt_component_question_answer_repo,
        s3_client=s3_client,
    )
