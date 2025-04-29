from typing import List

from app.core.config import rabbit_mq_settings
from app.domain.generation.schemas.generation.generation_job import GenerationJobInDB
from app.domain.generation.services.calculate_remaining_time import CalculateRemainingTimeService
from app.core.errors.exceptions import NoInferenceConsumerException, NoUpscaleConsumerException
from app.application.generation.request.dto.generation_mq import ImageInfo, GenerationPublishMessage
from app.domain.generation.dto.request_generation import RequestGenerationDto, PromptComponentAnswer
from app.domain.generation.services.build_prompt import replace_hair_with_ohwx_hair, BuildPromptService
from app.infrastructure.google_genai.genai_api import async_gemini_translate_prompt
from app.domain.common.enums.gender import Gender
from app.domain.generation.services.calculate_token import calculate_required_token
from app.application.generation.request.dto.request import CalculateTokenRequest, CalculateTokenResponse
from app.core.errors.http_exceptions import UserHasNotEnoughTokenException
from app.domain.token.enums.token import TokenSourceType
from app.domain.token.models.token import TokenWallet
from app.domain.token.services.token_domain_sevice import TokenService
from app.domain.user.models.user import User
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.repositories.user.user import UserRepository
from app.application.transactional_service import TransactionalService
from app.domain.generation.services.generation_request_service import GenerationRequestService
from app.application.generation.request.dto.request import GenerationRequestRequest, GenerationRequestResponse


class RequestGenerationService(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            token_service: TokenService,
            calculate_remaining_time_service: CalculateRemainingTimeService,
            generation_request_serivce: GenerationRequestService,
            build_prompt_service: BuildPromptService,
            rabbit_mq_service: RabbitMQService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.token_domain_service = token_service
        self.calculate_remaining_time_service = calculate_remaining_time_service
        self.generation_request_serivce = generation_request_serivce
        self.build_prompt_service = build_prompt_service
        self.rabbit_mq_service = rabbit_mq_service

    def calculate_required_token(self, request: CalculateTokenRequest) -> CalculateTokenResponse:
        return CalculateTokenResponse(
            token=calculate_required_token(request.is_high_res, request.is_user_hair_model)
        )

    async def request_generation(
            self,
            request: GenerationRequestRequest,
            user_id: int
    ) -> GenerationRequestResponse:
        message, response = await self._request_generation(request, user_id)
        await self._publish_message(message)
        return response


    @transactional
    async def _request_generation(
            self,
            request: GenerationRequestRequest,
            user_id: int
    ):
        # 생성 서버 연결 여부
        _, inference_consumer_count = await self.rabbit_mq_service.get_queue_info(rabbit_mq_settings.RABBITMQ_INFERENCE_CONSUME)
        if inference_consumer_count < 1:
            raise NoInferenceConsumerException()

        # 업스케일 서버 연결 여부
        _, upscale_consumer_count = await self.rabbit_mq_service.get_queue_info(rabbit_mq_settings.RABBITMQ_UPSCALE_CONSUME)
        if upscale_consumer_count < 1:
            raise NoUpscaleConsumerException()

        # 유저 토큰 충분한지 계산
        user_with_wallet: User = self.user_repo.get_with_token_wallets(user_id)
        token_wallet: TokenWallet = user_with_wallet.current_token_wallet

        consumed_token: int = calculate_required_token(request.is_high_res, request.is_user_hair_style)

        if not token_wallet.has_available_token(consumed_token):
            raise UserHasNotEnoughTokenException()

        # 프롬프트 제작
        english_prompt = await self._build_prompt(request)

        # 예상 이미지 생성 만료 시간
        generation_job_expire_time = self.calculate_remaining_time_service.get_generation_job_expire_time(
            is_high_resolution=request.is_high_res,
            generation_consumer_count=inference_consumer_count,
            upscale_consumer_count=upscale_consumer_count,
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

        # 메시지 및 응답 생성
        generation_job_indb = GenerationJobInDB.model_validate(generation_job)
        message = GenerationPublishMessage(
            image_info_list=[
                ImageInfo(
                    generated_image_id=generated_image.id,
                    s3_key=generated_image.s3_key,
                )
                for generated_image in generated_images
            ],
            **generation_job_indb.model_dump(),
            time_to_live_sec=generation_job_expire_time,
            generation_job_id=generation_job.id,
        )
        
        response = GenerationRequestResponse(
            generation_request_id=generation_request.id,
            remaining_sec=generation_job_expire_time,
        )
        return message, response


    async def _build_prompt(
            self,
            request: GenerationRequestRequest,
    ) -> str:

        # 한국어 프롬프트 제작
        gender: Gender = self.generation_request_serivce.get_gender_by_hair_style(**request.model_dump())
        korean_prompt = self.build_prompt_service.build_korean_prompt(
            gender=gender,
            prompt_component_answers=request.prompt_component_answers,
        )
        # 영어 번역
        english_prompt = await async_gemini_translate_prompt(korean_prompt)

        # 영어 프롬프트 조정
        return replace_hair_with_ohwx_hair(english_prompt)


    async def _publish_message(
            self,
            message: GenerationPublishMessage,
    ):
        await self.rabbit_mq_service.publish(
            message=message.model_dump_json(),
            queue_name=rabbit_mq_settings.RABBITMQ_INFERENCE_PUBLISH,
            expiration_sec=message.time_to_live_sec,
        )


from fastapi import Depends
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.domain.token.services.token_domain_sevice import get_token_service
from app.domain.generation.services.calculate_remaining_time import get_calculate_remaining_time_service
from app.domain.generation.services.generation_request_service import get_generation_request_service
from app.domain.generation.services.build_prompt import get_build_prompt_service

def get_request_generation_service(
        user_repo: UserRepository = Depends(get_user_repository),
        token_service: TokenService = Depends(get_token_service),
        calculate_remaining_time_service: CalculateRemainingTimeService = Depends(get_calculate_remaining_time_service),
        generation_request_serivce: GenerationRequestService = Depends(get_generation_request_service),
        build_prompt_service: BuildPromptService = Depends(get_build_prompt_service),
        rabbit_mq_service: RabbitMQService = Depends(get_rabbit_mq_service),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> RequestGenerationService:
    return RequestGenerationService(
        user_repo=user_repo,
        token_service=token_service,
        calculate_remaining_time_service=calculate_remaining_time_service,
        generation_request_serivce=generation_request_serivce,
        build_prompt_service=build_prompt_service,
        rabbit_mq_service=rabbit_mq_service,
        unit_of_work=unit_of_work,
    )

