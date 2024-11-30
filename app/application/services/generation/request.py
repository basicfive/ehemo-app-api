from typing import List, Optional
from fastapi import Depends

from app.domain.hair_model.models.scene import ImageResolution
from app.application.services.generation.dto.request import CreateGenerationRequestRequest, \
    GenerationRequestResponse
from app.application.services.generation.dto.mq import MQPublishMessage
from app.core.config import image_generation_setting, aws_s3_setting
from app.core.enums.generation_status import GenerationStatusEnum, GenerationResultEnum
from app.core.errors.exceptions import NoInferenceConsumerException
from app.core.errors.http_exceptions import UnauthorizedException, ConcurrentGenerationRequestError, \
    UserHasNotEnoughTokenException
from app.core.utils import generate_unique_datatime_uuid_key
from app.domain.generation.models.generation import GenerationRequest
from app.domain.generation.schemas.generation_request import GenerationRequestCreate, GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobCreate, ImageGenerationJobInDB, \
    ImageGenerationJobUpdate
from app.domain.generation.services.generation_domain_service import estimate_normal_priority_message_wait_sec, \
    calculate_normal_message_ttl_sec, is_generation_in_progress
from app.domain.hair_model.models.hair import HairVariantModel, Length, SpecificColor
from app.domain.hair_model.services.hair_model_prompt import create_prompts
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserUpdate
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService, get_rabbit_mq_service
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, \
    ImageGenerationJobRepository, get_generation_request_repository, get_image_generation_job_repository
from app.infrastructure.repositories.hair_model.hair_model import HairVariantModelRepository, \
    PostureAndClothingRepository, SpecificColorRepository, get_specific_color_repository, \
    get_posture_and_clothing_repository, get_hair_variant_model_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository
from datetime import datetime, UTC, timedelta

# TODO: DB 접근마다 에러처리 / TRANSACTION
class RequestGenerationApplicationService:
    def __init__(
            self,
            user_repo: UserRepository,
            specific_color_repo: SpecificColorRepository,
            posture_and_clothing_repo: PostureAndClothingRepository,
            hair_variant_model_repo: HairVariantModelRepository,
            generation_request_repo: GenerationRequestRepository,
            image_generation_job_repo: ImageGenerationJobRepository,
            rabbit_mq_service: RabbitMQService
    ):
        self.user_repo = user_repo
        self.specific_color_repo = specific_color_repo
        self.posture_and_clothing_repo = posture_and_clothing_repo
        self.hair_variant_model_repo = hair_variant_model_repo
        self.generation_request_repo = generation_request_repo
        self.image_generation_job_repo = image_generation_job_repo
        self.rabbit_mq_service = rabbit_mq_service

    def cancel_generation(
            self,
            generation_request_id: int,
            user_id: int,
    ):
        generation_request: GenerationRequest = self.generation_request_repo.get(generation_request_id)
        if generation_request.user_id != user_id:
            raise UnauthorizedException()
        self.generation_request_repo.update(
            obj_id=generation_request.id,
            obj_in=GenerationRequestUpdate(
                generation_result=GenerationResultEnum.CANCELED
            )
        )

    # TODO: 1회 메서드 실행 시 db 9 + 10 회 (10번은 job create x 10)
    async def request_generation(
            self,
            request: CreateGenerationRequestRequest,
            user_id: int
    ) -> GenerationRequestResponse:

        if self._is_generation_in_progress(user_id):
            raise ConcurrentGenerationRequestError(context="Image generation already in progress.")

        # TODO: (urgent) id에 해당하는 user 존재하는 레코드인지 에러 처리필요
        user: User = self.user_repo.get(user_id)
        if not user.has_enough_token():
            raise UserHasNotEnoughTokenException()

        generation_request: GenerationRequest = self._create_generation_request(request, user_id)
        return await self._start_generation(generation_request.id, user)

    def _is_generation_in_progress(self, user_id: int) -> bool:
        latest_generation_request: Optional[GenerationRequest] = (
            self.generation_request_repo.get_latest_generation_request_by_user(user_id=user_id)
        )
        return is_generation_in_progress(latest_generation_request)

    def _create_generation_request(
            self,
            request: CreateGenerationRequestRequest,
            user_id: int
    ) -> GenerationRequest:
        hair_variant_model: HairVariantModel = (
            self.hair_variant_model_repo.get_by_hair_style_length_color(
                hair_style_id=request.hair_style_id,
                length_id=request.length_id,
                color_id=request.color_id,
            )
        )
        return self.generation_request_repo.create(
            obj_in=GenerationRequestCreate(
                user_id=user_id,
                hair_variant_model_id=hair_variant_model.id,
                background_id=request.background_id,
                image_resolution_id=request.image_resolution_id
            )
        )

    # TODO: 에러처리
    async def _start_generation(
            self,
            generation_request_id: int,
            user: User,
    ) -> GenerationRequestResponse:
        """
        1. Prompt 를 n개 생성한다.
        2. image_generation_job 을 생성한다.
        3. mq 서버에 생성 요청을 보낸다.
        4. 2 - 3 프롬프트 갯수만큼 반복
        """

        generation_request_with_relation: GenerationRequest = (
            self.generation_request_repo.get_with_all_relations(generation_request_id)
        )

        # create prompt list
        prompt_list = self._create_prompts(generation_request_with_relation)

        # queue 상태 확인
        message_count, consumer_count = await self.rabbit_mq_service.get_queue_info()
        if consumer_count < 1:
            raise NoInferenceConsumerException()

        message_time_to_live_sec = estimate_normal_priority_message_wait_sec(
            image_count=message_count,
            processor_count=consumer_count
        )

        for idx, prompt in enumerate(prompt_list):
            message_time_to_live_sec += calculate_normal_message_ttl_sec()
            # job 생성
            image_generation_job = self._create_image_generation_job(
                prompt=prompt,
                image_resolution=generation_request_with_relation.image_resolution,
                time_to_live_sec=message_time_to_live_sec,
                generation_request_id=generation_request_with_relation.id
            )
            # MQ 요청 보내기
            await self._publish_job_as_mq_message(image_generation_job, message_time_to_live_sec)

        # 사용자 토큰 감소
        self.user_repo.update(obj_id=user.id, obj_in=UserUpdate(token=user.token - 1))

        message_count, consumer_count = await self.rabbit_mq_service.get_queue_info()
        return GenerationRequestResponse(
            generation_request_id=generation_request_with_relation.id,
            remaining_sec=estimate_normal_priority_message_wait_sec(image_count=message_count, processor_count=consumer_count),
            generated_image_cnt_per_request=image_generation_setting.GENERATED_IMAGE_CNT_PER_REQUEST
        )

    def _create_prompts(self, generation_request_with_relations: GenerationRequest) -> List[str]:

        hair_variant_model_with_relations: HairVariantModel = generation_request_with_relations.hair_variant_model

        posture_and_clothing_list = self.posture_and_clothing_repo.get_random_records_in_gender(
            gender_id=generation_request_with_relations.hair_variant_model.gender.id,
            limit=image_generation_setting.GENERATED_IMAGE_CNT_PER_REQUEST
        )
        specific_color_list: List[SpecificColor] = self.specific_color_repo.get_all_by_color_limit(
            hair_variant_model_with_relations.color_id,
            limit=image_generation_setting.GENERATED_IMAGE_CNT_PER_REQUEST
        )

        # null length 수정 - hs 기본 길이로 변경한다.
        if hair_variant_model_with_relations.hair_style.has_length_option:
            length: Length = hair_variant_model_with_relations.length
        else :
            length: Length = hair_variant_model_with_relations.hair_style.length

        return create_prompts(
            length=length,
            gender=hair_variant_model_with_relations.gender,
            background=generation_request_with_relations.background,
            lora_model=hair_variant_model_with_relations.lora_model,
            specific_color_list=specific_color_list,
            posture_and_clothing_list=posture_and_clothing_list,
            count=image_generation_setting.GENERATED_IMAGE_CNT_PER_REQUEST
        )

    def _create_image_generation_job(
            self,
            prompt: str,
            image_resolution: ImageResolution,
            time_to_live_sec: int,
            generation_request_id: int,
    ) -> ImageGenerationJobInDB:
        s3_key = generate_unique_datatime_uuid_key(prefix=aws_s3_setting.GENERATED_IMAGE_S3KEY_PREFIX)
        return ImageGenerationJobInDB.model_validate(
            self.image_generation_job_repo.create(
                obj_in=ImageGenerationJobCreate(
                    retry_count=0,
                    expires_at=datetime.now(UTC) + timedelta(seconds=time_to_live_sec),
                    prompt=prompt,
                    distilled_cfg_scale=image_generation_setting.DISTILLED_CFG_SCALE,
                    width=image_resolution.width,
                    height=image_resolution.height,
                    generation_request_id=generation_request_id,
                    s3_key=s3_key
                )
            )
        )

    async def _publish_job_as_mq_message(
            self,
            image_generation_job: ImageGenerationJobInDB,
            time_to_live_sec: int
    ):
        message = MQPublishMessage(
            **image_generation_job.model_dump(),
            image_generation_job_id=image_generation_job.id,
        )
        await self.rabbit_mq_service.publish(message=message, expiration_sec=time_to_live_sec)
        self.image_generation_job_repo.update(
            obj_id=image_generation_job.id,
            obj_in=ImageGenerationJobUpdate(status=GenerationStatusEnum.PROCESSING)
        )


def get_request_generation_application_service(
        user_repo: UserRepository = Depends(get_user_repository),
        specific_color_repo: SpecificColorRepository = Depends(get_specific_color_repository),
        posture_and_clothing_repo: PostureAndClothingRepository = Depends(get_posture_and_clothing_repository),
        hair_variant_model_repo: HairVariantModelRepository = Depends(get_hair_variant_model_repository),
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        image_generation_job_repo: ImageGenerationJobRepository = Depends(get_image_generation_job_repository),
        rabbit_mq_service: RabbitMQService = Depends(get_rabbit_mq_service)
) -> RequestGenerationApplicationService:
    return RequestGenerationApplicationService(
        user_repo=user_repo,
        specific_color_repo=specific_color_repo,
        posture_and_clothing_repo=posture_and_clothing_repo,
        hair_variant_model_repo=hair_variant_model_repo,
        generation_request_repo=generation_request_repo,
        image_generation_job_repo=image_generation_job_repo,
        rabbit_mq_service=rabbit_mq_service
    )

