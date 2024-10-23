from typing import List
from fastapi import Depends
from app.application.query.hair_model_query import HairModelQueryService, HairModelDetails, get_hair_model_query_service
from app.application.services.generation.dto.create_generation_request import CreateGenerationRequestRequest, \
    CreateGenerationRequestResponse
from app.application.services.generation.dto.mq import MQPublishMessage
from app.core.constants import SINGLE_INFERENCE_IMAGE_CNT, DISTILLED_CFG_SCALE
from app.core.enums.generation_status import GenerationStatusEnum
from app.core.utils import generate_unique_s3_key
from app.domain.generation.schemas.generation_request import GenerationRequestCreate, GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobCreate, ImageGenerationJobInDB, \
    ImageGenerationJobUpdate
from app.domain.generation.services.generation_domain_service import calculate_generation_sec
from app.domain.hair_model.models.hair import HairVariantModel, Length
from app.domain.hair_model.schemas.hair.gender import GenderInDB
from app.domain.hair_model.schemas.hair.hair_style import HairStyleInDB
from app.domain.hair_model.schemas.hair.length import LengthInDB
from app.domain.hair_model.schemas.hair.color import ColorInDB
from app.domain.hair_model.schemas.scene.background import BackgroundInDB
from app.domain.hair_model.schemas.scene.image_resolution import ImageResolutionInDB
from app.domain.hair_model.services.hair_model_prompt import create_prompts
from app.domain.user.models.user import User
from app.domain.user.schemas.user import UserInDB
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService, get_rabbit_mq_service
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository, \
    ImageGenerationJobRepository, get_generation_request_repository, get_image_generation_job_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository


class RequestGenerationApplicationService:
    def __init__(
            self,
            user_repo: UserRepository,
            hair_model_query_service: HairModelQueryService,
            generation_request_repo: GenerationRequestRepository,
            image_generation_job_repo: ImageGenerationJobRepository,
            # rabbit_mq_service: RabbitMQService
    ):
        self.user_repo = user_repo
        self.hair_model_query_service = hair_model_query_service
        self.generation_request_repo = generation_request_repo
        self.image_generation_job_repo = image_generation_job_repo
        # self.rabbit_mq_service = rabbit_mq_service

    def create_generation_request(
            self,
            request: CreateGenerationRequestRequest
    ) -> CreateGenerationRequestResponse:

        # TODO: DB 접근마다 에러처리
        hair_variant_model: HairVariantModel = (
            self.hair_model_query_service.get_hair_variant_model_by_hair_style_length_color(
                hair_style_id=request.hair_style_id,
                length_id=request.length_id,
                color_id=request.color_id,
            )
        )
        generation_request = self.generation_request_repo.create(
            obj_in=GenerationRequestCreate(
                user_id=request.user_id,
                hair_variant_model_id=hair_variant_model.id,
                background_id=request.background_id,
                image_resolution_id=request.image_resolution_id
            )
        )

        hair_model_details: HairModelDetails = (
            self.hair_model_query_service.get_hair_model_details(
                hair_variant_model_id=generation_request.hair_variant_model_id,
                background_id=generation_request.background_id,
                image_resolution_id=generation_request.image_resolution_id
            )
        )

        user: User = self.user_repo.get(obj_id=request.user_id)

        return CreateGenerationRequestResponse(
            generation_request_id=generation_request.id,
            user=UserInDB.model_validate(user),
            gender=GenderInDB.model_validate(hair_model_details.gender),
            hair_style=HairStyleInDB.model_validate(hair_model_details.hair_style),
            length=LengthInDB.model_validate(hair_model_details.length),
            color=ColorInDB.model_validate(hair_model_details.color),
            background=BackgroundInDB.model_validate(hair_model_details.background),
            image_resolution=ImageResolutionInDB.model_validate(hair_model_details.image_resolution)
        )

    # TODO: 수정 사항 반영하는 코드는 어떻게 깔끔하게 짤지 다시 생각해보자.
    def update_generation_request(self, generation_request_id: int, generation_request_update: GenerationRequestUpdate):
        pass
        # generation_request:GenerationRequest = self.generation_request_repo.update(
        #     obj_id=generation_request_id,
        #     obj_in=generation_request_update
        # )
        # hair_model_details: HairModelDetails = (
        #     self.hair_model_query_service.get_hair_model_details(
        #         hair_variant_model_id=generation_request.hair_variant_model_id,
        #         background_id=generation_request.background_id,
        #         image_resolution_id=generation_request.image_resolution_id
        #     )
        # )
        # return CreateGenerationRequestResponse(
        #     generation_request_id=generation_request.id,
        #     user=self.user_repo.get(obj_id=request.user_id),
        #     **hair_model_details.model_dump()
        # )


    def start_generation(self, generation_request_id: int):
        """
        1. 사용자 토큰 validation을 진행한다. - 토큰이 충분하지 않은 경우 에러 처리
        2. image_generation_job n개 생성한다.
        3. 각각을 사용해서 mq 서버에 생성 요청을 보낸다.
        :param generation_request_id:
        :return:
        """
        generation_request = self.generation_request_repo.get(generation_request_id)
        user = self.user_repo.get(generation_request.user_id)

        if not user.has_enough_token():
            # TODO 커스텀 에러
            raise ValueError("사용자 토큰 없음")

        # prompt 10개 생성
        hair_model_details: HairModelDetails = (
            self.hair_model_query_service.get_hair_model_details(
                hair_variant_model_id=generation_request.hair_variant_model_id,
                background_id=generation_request.background_id,
                image_resolution_id=generation_request.image_resolution_id
            )
        )
        posture_and_clothing_list=self.hair_model_query_service.get_random_posture_and_clothing(limit=SINGLE_INFERENCE_IMAGE_CNT)

        # null length 수정 - hs 기본 길이로 변경한다.
        if not hair_model_details.hair_style.has_length_option:
            hair_model_details.length = self.hair_model_query_service.get_length_by_hair_style(hair_style_id=hair_model_details.hair_style.id)

        prompt_list: List[str] = create_prompts(
            length=hair_model_details.length,
            gender=hair_model_details.gender,
            background=hair_model_details.background,
            lora_model=hair_model_details.lora_model,
            specific_color_list=hair_model_details.specific_color_list,
            posture_and_clothing_list=posture_and_clothing_list,
            count=SINGLE_INFERENCE_IMAGE_CNT
        )

        # image_generation_job 10개 생성
        # TODO: transaction
        # TODO: 에러처리
        image_generation_job_list: List[ImageGenerationJobInDB] = []
        for prompt in prompt_list:
            db_image_generation_job = self.image_generation_job_repo.create(
                obj_in=ImageGenerationJobCreate(
                    prompt=prompt,
                    distilled_cfg_scale=DISTILLED_CFG_SCALE,
                    width=hair_model_details.image_resolution.width,
                    height=hair_model_details.image_resolution.height,
                    generation_request_id=generation_request_id
                )
            )
            image_generation_job_list.append(ImageGenerationJobInDB.model_validate(db_image_generation_job))

        for image_generation_job in image_generation_job_list:
            print(image_generation_job.model_dump_json(indent=2))

        return 10

        # # MQ 요청 보내기
        # for image_generation_job in image_generation_job_list:
        #     message = MQPublishMessage(
        #         **image_generation_job.model_dump(),
        #         image_generation_job_id=image_generation_job.id,
        #         s3_key=generate_unique_s3_key()
        #     )
        #     self.rabbit_mq_service.publish(message=message)
        #     self.image_generation_job_repo.update(
        #         obj_id=image_generation_job.id,
        #         obj_in=ImageGenerationJobUpdate(status=GenerationStatusEnum.PROCESSING)
        #     )
        #
        # message_count, consumer_count = self.rabbit_mq_service.get_queue_info()
        # return calculate_generation_sec(image_count=message_count, processor_count=consumer_count)

def get_request_generation_application_service(
        user_repo: UserRepository = Depends(get_user_repository),
        hair_model_query_service: HairModelQueryService = Depends(get_hair_model_query_service),
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        image_generation_job_repo: ImageGenerationJobRepository = Depends(get_image_generation_job_repository),
        # rabbit_mq_service: RabbitMQService = Depends(get_rabbit_mq_service)
) -> RequestGenerationApplicationService:
    return RequestGenerationApplicationService(
        user_repo=user_repo,
        hair_model_query_service=hair_model_query_service,
        generation_request_repo=generation_request_repo,
        image_generation_job_repo=image_generation_job_repo,
        # rabbit_mq_service=rabbit_mq_service
    )