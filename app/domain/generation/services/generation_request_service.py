from typing import Tuple, Optional, List
from datetime import datetime, UTC, timedelta
import uuid
from app.core.config import image_generation_settings, aws_s3_settings
import logging

from app.domain.generation.services.request_number import generate_request_number
from app.domain.generation.models.generation import GenerationRequestResult, GenerationJobStatus
from app.domain.generation.enums.generated_image_status import GeneratedImageStatus
from app.domain.generation.schemas.generated_image.generated_image import GeneratedImageUpdate
from app.domain.generation.schemas.generation.generation_request import GenerationRequestUpdate
from app.domain.generation.schemas.generation.generation_job import GenerationJobUpdate
from app.domain.common.enums.gender import Gender
from app.domain.generation.schemas.generation.generation_request import GenerationRequestCreate
from app.domain.generation.dto.request_generation import RequestGenerationDto
from app.domain.generation.schemas.generated_image.generated_image import GeneratedImageCreate
from app.domain.generation.models.image_resolution import ImageResolution
from app.domain.generation.models.hair_style import HairStyle, HairStyleLora
from app.domain.training.models.user_hair_style import UserHairStyle, UserHairStyleLora
from app.domain.generation.schemas.generation.generation_job import GenerationJobCreate
from app.infrastructure.repositories.generation.generation import RequestPromptComponentQuestionAnswerRepository
from app.domain.generation.schemas.generation.request_prompt_component_question_answer import RequestPromptComponentQuestionAnswerCreate
from app.infrastructure.repositories.generation.image_resolution import ImageResolutionRepository
from app.domain.generation.models.generation import GenerationRequest, GenerationJob
from app.domain.generation.models.generated_image import GeneratedImage
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, GenerationJobRepository
from app.infrastructure.repositories.generation.generated_image import GeneratedImageRepository
from app.infrastructure.repositories.generation.hair_style import HairStyleRepository
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleRepository


logger = logging.getLogger(__name__)


class GenerationRequestService:
    def __init__(
            self,
            generation_request_repository: GenerationRequestRepository,
            generation_job_repository: GenerationJobRepository,
            generated_image_repository: GeneratedImageRepository,
            hair_style_repository: HairStyleRepository,
            user_hair_style_repository: UserHairStyleRepository,
            image_resolution_repository: ImageResolutionRepository,
            request_prompt_component_question_answer_repository: RequestPromptComponentQuestionAnswerRepository,
        ):
        self.generation_request_repository = generation_request_repository
        self.generation_job_repository = generation_job_repository
        self.generated_image_repository = generated_image_repository
        self.image_resolution_repository = image_resolution_repository
        self.hair_style_repository = hair_style_repository
        self.user_hair_style_repository = user_hair_style_repository
        self.request_prompt_component_question_answer_repository = request_prompt_component_question_answer_repository
    
    def mark_after_generation_success(self, generation_job_id: int) -> Tuple[GenerationJob, List[GeneratedImage]]:

        generation_job: GenerationJob = self.generation_job_repository.update_with_flush(
            obj_id=generation_job_id,
            obj_in=GenerationJobUpdate(
                status=GenerationJobStatus.PENDING_UPSCALE,
            )
        )

        generated_images: List[GeneratedImage] = self.generated_image_repository.get_all_by_generation_job_id(generation_job_id)
        for generated_image in generated_images:
            generated_image = self.generated_image_repository.update_with_flush(
                obj_id=generated_image.id,
                obj_in=GeneratedImageUpdate(
                    status=GeneratedImageStatus.GENERATED,
                )
            )
        return generation_job, generated_images
    
    def mark_as_success(self, generation_job_id: int) -> Tuple[GenerationRequest, GenerationJob, List[GeneratedImage]]:
        generation_job: GenerationJob = self.generation_job_repository.update_with_flush(
            obj_id=generation_job_id,
            obj_in=GenerationJobUpdate(
                status=GenerationJobStatus.COMPLETED,
            )
        )
        generation_request: GenerationRequest = self.generation_request_repository.update_with_flush(
            obj_id=generation_job.generation_request_id,
            obj_in=GenerationRequestUpdate(
                generation_result=GenerationRequestResult.SUCCEED,
            )
        )
        generated_images: List[GeneratedImage] = self.generated_image_repository.get_all_by_generation_job_id(generation_job_id)
        for generated_image in generated_images:
            generated_image = self.generated_image_repository.update_with_flush(
                obj_id=generated_image.id,
                obj_in=GeneratedImageUpdate(
                    status=GeneratedImageStatus.UPSCALED,
                )
            )
        return generation_request, generation_job, generated_images

    def mark_as_failed(self, generation_job_id: int) -> Tuple[GenerationRequest, GenerationJob, List[GeneratedImage]]:
        generation_job: GenerationJob = self.generation_job_repository.update_with_flush(
            obj_id=generation_job_id,
            obj_in=GenerationJobUpdate(
                status=GenerationJobStatus.FAILED,
            )
        )
        generation_request: GenerationRequest = self.generation_request_repository.update_with_flush(
            obj_id=generation_job.generation_request_id,
            obj_in=GenerationRequestUpdate(
                generation_result=GenerationRequestResult.FAILED,
            )
        )
        generated_images: List[GeneratedImage] = self.generated_image_repository.get_all_by_generation_job_id(generation_job_id)
        for generated_image in generated_images:
            generated_image = self.generated_image_repository.update_with_flush(
                obj_id=generated_image.id,
                obj_in=GeneratedImageUpdate(
                    status=GeneratedImageStatus.FAILED,
                )
            )
        return generation_request, generation_job, generated_images

    def get_gender_by_hair_style(
            self,
            is_user_hair_style: bool,
            user_hair_style_id: Optional[int] = None,
            hair_style_id: Optional[int] = None,
    ) -> Gender:
        if is_user_hair_style and not user_hair_style_id:
            raise ValueError("user_hair_style_id is required when is_user_hair_style is True")
        if not is_user_hair_style and not hair_style_id:
            raise ValueError("hair_style_id is required when is_user_hair_style is False")

        if is_user_hair_style:
            user_hair_style: UserHairStyle = self.user_hair_style_repository.get(user_hair_style_id)
            return user_hair_style.gender
        else:
            hair_style: HairStyle = self.hair_style_repository.get(hair_style_id)
            return hair_style.gender
        
    def _create_request_number(self) -> str:
        request_number = generate_request_number()
        while self.generation_request_repository.get_by_request_number(request_number):
            logger.info(f"request_number {request_number} already exists. generating new number")
            request_number = generate_request_number()
        return request_number

    def create_generation_request_job_image(
            self,
            user_id: int,
            request_dto: RequestGenerationDto,
            job_time_to_live_sec: int,
            final_generation_prompt: str,
            consumed_tokens: int,
    ) -> Tuple[GenerationRequest, GenerationJob, List[GeneratedImage]]:

        image_resolution: ImageResolution = self.image_resolution_repository.get_by_ratio_and_is_high_res(request_dto.image_ratio_id, request_dto.is_high_res)
        request_number = self._create_request_number()

        # 요청 생성
        generation_request: GenerationRequest = self.generation_request_repository.create_with_flush(
            obj_in=GenerationRequestCreate(
                **request_dto.model_dump(),
                user_id=user_id,
                request_number=request_number,
                image_resolution_id=image_resolution.id,
                final_generation_prompt=final_generation_prompt,
                consumed_tokens=consumed_tokens,
            ),
        )

        # 질문 응답에 대한 답변 저장
        for prompt_component_answer in request_dto.prompt_component_answers:
            self.request_prompt_component_question_answer_repository.create_with_flush(
                obj_in=RequestPromptComponentQuestionAnswerCreate(
                    generation_request_id=generation_request.id,
                    prompt_component_question_id=prompt_component_answer.prompt_component_question_id,
                    answer=prompt_component_answer.answer,
                ),
            )

        # 생성 작업 생성
        is_user_hair_style = generation_request.is_user_hair_style

        hair_lora_model_name = None
        user_hair_lora_model_s3_key = None

        if is_user_hair_style:
            user_hair_style: UserHairStyle = self.user_hair_style_repository.get_with_lora(generation_request.user_hair_style_id)
            user_hair_lora_model: UserHairStyleLora = user_hair_style.user_hair_style_lora
            hair_lora_model_name = user_hair_lora_model.lora_name
            user_hair_lora_model_s3_key = user_hair_lora_model.lora_s3_key
        else:
            hair_style: HairStyle = self.hair_style_repository.get_with_lora(generation_request.hair_style_id)
            hair_lora_model: HairStyleLora = hair_style.hair_style_lora
            hair_lora_model_name = hair_lora_model.lora_name
        
        width = image_resolution.width
        height = image_resolution.height

        generation_job: GenerationJob = self.generation_job_repository.create_with_flush(
            obj_in=GenerationJobCreate(
                expires_at=datetime.now(UTC) + timedelta(seconds=job_time_to_live_sec),

                image_count=image_generation_settings.GENERATED_IMAGE_CNT_PER_REQUEST,

                prompt=generation_request.final_generation_prompt,

                is_user_hair_style=generation_request.is_user_hair_style,
                user_hair_lora_model_s3_key=user_hair_lora_model_s3_key,
                hair_lora_model_name=hair_lora_model_name,

                distilled_cfg_scale=image_generation_settings.DISTILLED_CFG_SCALE,
                width=width,
                height=height,

                is_user_reference_image=generation_request.is_user_reference_image,
                user_reference_image_s3_key=generation_request.user_reference_image_s3_key,
                user_reference_image_denoise_strength=generation_request.user_reference_image_denoise_strength,

                generation_request_id=generation_request.id,
            ),
        )

        generated_images: List[GeneratedImage] = []
        for _ in range(image_generation_settings.GENERATED_IMAGE_CNT_PER_REQUEST):
            generated_image: GeneratedImage = self.generated_image_repository.create_with_flush(
                obj_in=GeneratedImageCreate(
                    generation_job_id=generation_job.id,
                    s3_key=aws_s3_settings.GENERATED_IMAGE_S3KEY_PREFIX + str(uuid.uuid4()),
                    user_id=generation_request.user_id,
                    upscaled_s3_key=aws_s3_settings.GENERATED_IMAGE_S3KEY_PREFIX + str(uuid.uuid4()),
                ),
            )
            generated_images.append(generated_image)

        return generation_request, generation_job, generated_images

from fastapi import Depends
from app.infrastructure.repositories.generation.generation import get_generation_request_repository
from app.infrastructure.repositories.generation.generation import get_generation_job_repository
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.repositories.generation.hair_style import get_hair_style_repository
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository
from app.infrastructure.repositories.generation.image_resolution import get_image_resolution_repository
from app.infrastructure.repositories.generation.generation import get_request_prompt_component_question_answer_repository

def get_generation_request_service(
        generation_request_repository: GenerationRequestRepository = Depends(get_generation_request_repository),
        generation_job_repository: GenerationJobRepository = Depends(get_generation_job_repository),
        generated_image_repository: GeneratedImageRepository = Depends(get_generated_image_repository),
        hair_style_repository: HairStyleRepository = Depends(get_hair_style_repository),
        user_hair_style_repository: UserHairStyleRepository = Depends(get_user_hair_style_repository),
        image_resolution_repository: ImageResolutionRepository = Depends(get_image_resolution_repository),
        request_prompt_component_question_answer_repository: RequestPromptComponentQuestionAnswerRepository = Depends(get_request_prompt_component_question_answer_repository),
) -> GenerationRequestService:
    return GenerationRequestService(
        generation_request_repository=generation_request_repository,
        generation_job_repository=generation_job_repository,
        generated_image_repository=generated_image_repository,
        hair_style_repository=hair_style_repository,
        user_hair_style_repository=user_hair_style_repository,
        image_resolution_repository=image_resolution_repository,
        request_prompt_component_question_answer_repository=request_prompt_component_question_answer_repository,
    )
