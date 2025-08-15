from typing import List, Optional
import logging

from app.core.config import base_settings
from app.infrastructure.alert.discord_webhook import send_error_notification
from app.infrastructure.s3.s3_client import S3Client
from app.domain.generation.schemas.generation.generation_job import GenerationJobInDB
from app.domain.generation.services.calculate_remaining_time import CalculateRemainingTimeService
from app.application.generation.request.dto.generation_mq import ImageInfo, GenerationPublishMessage
from app.domain.generation.dto.request_generation import RequestGenerationDto
from app.domain.generation.services.build_prompt import replace_hair_with_ohwx_hair, BuildPromptService
from app.domain.generation.services.reference_image_preprocess import ReferenceImagePreprocessService
from app.infrastructure.google_genai.genai_api import gemini_translate_prompt
from app.domain.common.enums.gender import Gender
from app.domain.generation.services.calculate_token import calculate_token_cost
from app.core.errors.http_exceptions import UserHasNotEnoughTokenException
from app.domain.token.enums.token import TokenSourceType
from app.domain.token.models.token import TokenWallet
from app.domain.token.services.token_domain_sevice import TokenService
from app.domain.user.models.user import User
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.repositories.user.user import UserRepository
from app.application.transactional_service import TransactionalService
from app.domain.generation.services.generation_request_service import GenerationRequestService
from app.application.generation.request.dto.request import GenerationRequestRequest, GenerationRequestResponse
from app.application.generation.request.dto.request import ImageUploadUrlDto
from app.domain.generation.services.reference_image import create_reference_image_s3_key
from app.infrastructure.runpod.runpod_inference import request_runpod
from app.infrastructure.runpod.dto import InferencePayload, Output
from app.core.config import base_settings
from app.domain.generation.models.generation import GenerationRequest
from app.domain.generation.models.generation import GenerationJob
from app.domain.generation.models.generated_image import GeneratedImage

class RequestGenerationService(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            token_service: TokenService,
            calculate_remaining_time_service: CalculateRemainingTimeService,
            generation_request_serivce: GenerationRequestService,
            build_prompt_service: BuildPromptService,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
            reference_image_preprocess_service: ReferenceImagePreprocessService,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.token_domain_service = token_service
        self.calculate_remaining_time_service = calculate_remaining_time_service
        self.generation_request_serivce = generation_request_serivce
        self.build_prompt_service = build_prompt_service
        self.s3_client = s3_client
        self.reference_image_preprocess_service = reference_image_preprocess_service

    def _maybe_downscale_reference_image(self, s3_key: str) -> None:
        try:
            image_bytes: Optional[bytes] = self.s3_client.get_object_bytes(s3_key)
            if not image_bytes:
                return
            processed: Optional[bytes] = self.reference_image_preprocess_service.maybe_downscale(image_bytes)
            if processed is None:
                return
            self.s3_client.upload_to_s3(key=s3_key, image_data=processed, image_format='JPEG')
        except Exception as e:
            logging.exception("Failed to downscale reference image: %s", e)
            send_error_notification(
                webhook_url=base_settings.ALERT_DISCORD_WEBHOOK,
                error=e,
            )

    def calculate_token_cost(self,
            is_high_res: bool,
            is_user_hair_model: bool,
    ) -> int:
        return calculate_token_cost(is_high_res, is_user_hair_model)
        
    def get_reference_image_upload_url(self) -> ImageUploadUrlDto:
        s3_key = create_reference_image_s3_key()
        upload_url = self.s3_client.create_put_presigned_url(s3_key=s3_key)
        return ImageUploadUrlDto(
            upload_url=upload_url,
            s3_key=s3_key,
        )

    def _build_runpod_request(
            self,
            generation_request: GenerationRequest,
            generation_job: GenerationJob,
            generated_images: List[GeneratedImage],
    ) -> InferencePayload:

        denoise = generation_job.user_reference_image_denoise_strength 
        if denoise is None:
            denoise = 1.0
        if generation_job.is_user_reference_image:
            image_url = self.s3_client.create_get_presigned_url(generation_job.user_reference_image_s3_key)
            width = None
            height = None
        else:
            image_url = None
            width = generation_job.width
            height = generation_job.height
        
        return InferencePayload(
            job_id=generation_job.id,
            webhook_url=f"{base_settings.SERVER_ENDPOINT}{base_settings.API_V1_STR}/prod/generation/webhook/runpod",
            outputs=[
                Output(
                    upload_url=self.s3_client.create_put_presigned_url(generated_image.upscaled_s3_key),
                    image_format="JPEG",
                )
                for generated_image in generated_images
            ],
            is_img2img=generation_request.is_user_reference_image,
            image_url=image_url,
            width=width,
            height=height,
            iterations=generation_job.image_count,
            is_upscale=generation_job.is_high_res,
            prompt=generation_job.prompt,
            lora_name=f"{generation_job.lora_model_name}.safetensors", # TODO: 하드 코딩 개선
            denoise=denoise,
        )
        

    @transactional
    def request_generation(
            self,
            request: GenerationRequestRequest,
            user_id: int
    ) -> GenerationRequestResponse:

        # 유저 토큰 충분한지 계산
        user_with_wallet: User = self.user_repo.get_with_token_wallets(user_id)
        token_wallet: TokenWallet = user_with_wallet.current_token_wallet

        consumed_token: int = calculate_token_cost(request.is_high_res, request.is_user_hair_style)

        if not token_wallet.has_available_token(consumed_token):
            raise UserHasNotEnoughTokenException()

        # 참조 이미지가 있으면 필요 시 다운스케일 후 동일 키로 덮어쓰기
        if request.is_user_reference_image and request.user_reference_image_s3_key:
            self._maybe_downscale_reference_image(request.user_reference_image_s3_key)

        # 프롬프트 제작
        english_prompt = self._build_prompt(request)

        # 예상 이미지 생성 만료 시간
        generation_job_expire_time = self.calculate_remaining_time_service.get_generation_job_expire_time(
            is_high_resolution=request.is_high_res,
        )

        # 생성 요청, 생성 작업, 생성 이미지 생성
        generation_request, generation_job, generated_images = self.generation_request_serivce.create_generation_request_job_image(
            request_dto=RequestGenerationDto(**request.model_dump()),
            user_id=user_id,
            job_time_to_live_sec=generation_job_expire_time,
            final_generation_prompt=english_prompt,
            consumed_tokens=consumed_token,
        )

        # 토큰 소모
        self.token_domain_service.consume_token(
            token_wallet=token_wallet,
            amount=consumed_token,
            source_type=TokenSourceType.IMAGE_GENERATION,
        )

        # 메시지 생성
        generation_job_indb = GenerationJobInDB.model_validate(generation_job)

        payload = self._build_runpod_request(
            generation_request=generation_request,
            generation_job=generation_job,
            generated_images=generated_images,
        )

        # 생성 요청 전송
        request_runpod(payload=payload)

        return GenerationRequestResponse(
            generation_request_id=generation_request.id,
            remaining_sec=generation_job_expire_time,
        )


    def _build_prompt(
            self,
            request: GenerationRequestRequest,
    ) -> str:
        # 한국어 프롬프트 제작
        gender: Gender = self.generation_request_serivce.get_gender_by_hair_style(
            is_user_hair_style=request.is_user_hair_style,
            user_hair_style_id=request.user_hair_style_id,
            hair_style_id=request.hair_style_id,
        )
        korean_prompt = self.build_prompt_service.build_korean_prompt(
            gender=gender,
            prompt_component_answers=request.prompt_component_answers,
        )
        # 영어 번역
        english_prompt = gemini_translate_prompt(korean_prompt)

        # 영어 프롬프트 조정
        return replace_hair_with_ohwx_hair(english_prompt)


from fastapi import Depends
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.domain.token.services.token_domain_sevice import get_token_service
from app.domain.generation.services.calculate_remaining_time import get_calculate_remaining_time_service
from app.domain.generation.services.generation_request_service import get_generation_request_service
from app.domain.generation.services.build_prompt import get_build_prompt_service
from app.infrastructure.s3.s3_client import get_s3_client
from app.domain.generation.services.reference_image_preprocess import get_reference_image_preprocess_service

def get_request_generation_service(
        user_repo: UserRepository = Depends(get_user_repository),
        token_service: TokenService = Depends(get_token_service),
        calculate_remaining_time_service: CalculateRemainingTimeService = Depends(get_calculate_remaining_time_service),
        generation_request_serivce: GenerationRequestService = Depends(get_generation_request_service),
        build_prompt_service: BuildPromptService = Depends(get_build_prompt_service),
        s3_client: S3Client = Depends(get_s3_client),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
        reference_image_preprocess_service: ReferenceImagePreprocessService = Depends(get_reference_image_preprocess_service),
) -> RequestGenerationService:
    return RequestGenerationService(
        user_repo=user_repo,
        token_service=token_service,
        calculate_remaining_time_service=calculate_remaining_time_service,
        generation_request_serivce=generation_request_serivce,
        build_prompt_service=build_prompt_service,
        s3_client=s3_client,
        unit_of_work=unit_of_work,
        reference_image_preprocess_service=reference_image_preprocess_service,
    )

