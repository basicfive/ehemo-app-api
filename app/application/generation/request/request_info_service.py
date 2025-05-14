from fastapi.params import Depends
from typing import List, Optional, Dict
from datetime import datetime, timedelta, UTC
from collections import defaultdict

from app.infrastructure.database.unit_of_work import UnitOfWork
from app.domain.generation.schemas.generation.generation_request import GenerationRequestUpdate
from app.infrastructure.database.transaction import transactional
from app.domain.generation.models.generated_image import GeneratedImage
from app.application.generation.request.dto.request_info import GenerationRequestInfoPreview
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
from app.infrastructure.repositories.generation.generated_image import GeneratedImageRepository
from app.infrastructure.s3.s3_client import S3Client

class GenerationRequestInfoService(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            generation_request_repo: GenerationRequestRepository,
            image_ratio_repo: ImageRatioRepository,
            generation_job_repo: GenerationJobRepository,
            generated_image_repo: GeneratedImageRepository,
            request_prompt_component_question_answer_repo: RequestPromptComponentQuestionAnswerRepository,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.generation_request_repo = generation_request_repo
        self.generation_job_repo = generation_job_repo
        self.image_ratio_repo = image_ratio_repo
        self.generated_image_repo = generated_image_repo
        self.request_prompt_component_question_answer_repo = request_prompt_component_question_answer_repo
        self.s3_client = s3_client

    # TODO: 함수 완성
    def get_generation_request_status(self, generation_request_id: int, user_id: int):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise AccessUnauthorizedException()
    
    @transactional
    def update_request_is_favorite(self, generation_request_id: int, user_id: int, is_favorite: bool):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise AccessUnauthorizedException()
        self.generation_request_repo.update(
            obj_id=generation_request_id,
            obj_in=GenerationRequestUpdate(
                is_favorite=is_favorite,
            )
        )
        
    def get_all_user_generation_request_preview(self, user_id: int) -> List[GenerationRequestInfoPreview]:
        generation_requests: List[GenerationRequest] = self.generation_request_repo.get_all_by_user_with_hair_style(user_id)
        generation_requests = sorted(generation_requests, key=lambda x: x.created_at, reverse=True)

        generation_jobs: List[GenerationJob] = self.generation_job_repo.get_all_in_generation_requests(
            [generation_request.id for generation_request in generation_requests]
        )

        # 프롬프트 컴포넌트 답변 가져오기
        request_prompt_component_question_answers: List[RequestPromptComponentQuestionAnswer] = sorted(
            self.request_prompt_component_question_answer_repo.get_all_in_generation_requests(
                [generation_request.id for generation_request in generation_requests]
            ), 
            key=lambda x: x.prompt_component_question_id,
        )
        request_prompt_component_question_answers_dict: Dict[int, List[RequestPromptComponentQuestionAnswer]] = defaultdict(list)
        for request_prompt_component_question_answer in request_prompt_component_question_answers:
            request_prompt_component_question_answers_dict[request_prompt_component_question_answer.generation_request_id].append(request_prompt_component_question_answer)

        generated_images: List[GeneratedImage] = self.generated_image_repo.get_all_in_generation_jobs_with_job([generation_job.id for generation_job in generation_jobs])
        generated_images_dict: Dict[int, GeneratedImage] = {generated_image.generation_job.generation_request_id: generated_image for generated_image in generated_images}

        generation_request_infos: List[GenerationRequestInfoPreview] = []
        for generation_request in generation_requests:

            # 헤어스타일 이름 가져오기
            if generation_request.is_user_hair_style:
                user_hair_style: UserHairStyle = generation_request.user_hair_style
                hair_style_name = user_hair_style.title
            else:
                hair_style: HairStyle = generation_request.hair_style
                hair_style_name = hair_style.title

            # 프롬프트 컴포넌트 답변 가져오기
            selected_options: str = ""
            for request_prompt_component_question_answer in request_prompt_component_question_answers_dict[generation_request.id]:
                selected_options += f"{request_prompt_component_question_answer.answer}, "

            # 생성된 대표 이미지            
            thumbnail_url: str = self.s3_client.create_get_presigned_url(generated_images_dict[generation_request.id].s3_key)

            generation_request_infos.append(
                GenerationRequestInfoPreview(
                    generation_request_id=generation_request.id,
                    hair_style_name=hair_style_name,
                    thumbnail_url=thumbnail_url,
                    selected_options=selected_options,
                    created_at=generation_request.created_at,
                    generation_result=generation_request.generation_result,
                    is_favorite=generation_request.is_favorite,
                )
            )
        return generation_request_infos

    def get_generated_request_info(self, generation_request_id: int, user_id: int) -> GenerationRequestInfo:
        
        # validation
        generation_request_w_relations: GenerationRequest = self.generation_request_repo.get_with_relations(generation_request_id)
        if generation_request_w_relations.user_id != user_id:
            raise AccessUnauthorizedException()

        # 남은 시간 계산
        generation_job: GenerationJob = self.generation_job_repo.get_by_generation_request(generation_request_w_relations.id)
        time_delta: timedelta = generation_job.expires_at - datetime.now(UTC)
        remaining_sec: int = int(time_delta.total_seconds())

        # 헤어스타일 옵션 가져오기
        if generation_request_w_relations.is_user_hair_style:
            user_hair_style: UserHairStyle = generation_request_w_relations.user_hair_style
            user_hair_style_indb: UserHairStyleInDB = UserHairStyleInDB.model_validate(user_hair_style)
            selected_hair_style_option = HairStyleOption(
                is_user_hair_style=True,
                **user_hair_style_indb.model_dump(),
                thumbnail_url=self.s3_client.create_get_presigned_url(user_hair_style.thumbnail_s3_key),
            )
        else:
            hair_style: HairStyle = generation_request_w_relations.hair_style
            hair_style_indb: HairStyleInDB = HairStyleInDB.model_validate(hair_style)
            selected_hair_style_option = HairStyleOption(
                is_user_hair_style=False,
                **hair_style_indb.model_dump(),
                thumbnail_url=self.s3_client.create_get_presigned_url(hair_style.thumbnail_s3_key),
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
                    is_not_selected=False,
                    answer=request_prompt_component_question_answer.answer,
                )
            )

        # 이미지 비율 옵션 가져오기
        image_resolution: ImageResolution = generation_request_w_relations.image_resolution
        image_ratio: ImageRatio = self.image_ratio_repo.get(image_resolution.image_ratio_id)
        image_ratio_indb = ImageRatioInDB.model_validate(image_ratio)

        selected_image_ratio_option = ImageRatioOption(
            **image_ratio_indb.model_dump(),
            thumbnail_url=self.s3_client.create_get_presigned_url(image_ratio.thumbnail_s3_key),
        )

        generation_request_indb: GenerationRequestInDB = GenerationRequestInDB.model_validate(generation_request_w_relations)

        generated_image: GeneratedImage = self.generated_image_repo.get_any_by_generation_job_id(generation_job.id)

        return GenerationRequestInfo(
            **generation_request_indb.model_dump(),
            generation_request_id=generation_request_w_relations.id,
            remaining_sec=remaining_sec,
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
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.database.unit_of_work import get_unit_of_work

def get_generation_request_info_service(
    user_repo: UserRepository = Depends(get_user_repository),
    generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
    image_ratio_repo: ImageRatioRepository = Depends(get_image_ratio_repository),
    generation_job_repo: GenerationJobRepository = Depends(get_generation_job_repository),
    generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
    request_prompt_component_question_answer_repo: RequestPromptComponentQuestionAnswerRepository = Depends(get_request_prompt_component_question_answer_repository),
    s3_client: S3Client = Depends(get_s3_client),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> GenerationRequestInfoService:
    return GenerationRequestInfoService(
        user_repo=user_repo,
        generation_request_repo=generation_request_repo,
        image_ratio_repo=image_ratio_repo,
        generation_job_repo=generation_job_repo,
        generated_image_repo=generated_image_repo,
        request_prompt_component_question_answer_repo=request_prompt_component_question_answer_repo,
        s3_client=s3_client,
        unit_of_work=unit_of_work,
    )
