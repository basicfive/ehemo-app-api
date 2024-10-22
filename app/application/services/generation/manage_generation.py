import json
from typing import List
from fastapi import Depends
from app.application.services.generation.dto.mq import MQConsumeMessage
from app.core.enums.generation_status import GenerationStatusEnum
from app.domain.generation.models.generation import ImageGenerationJob
from app.domain.generation.models.image import GeneratedImageGroup, GeneratedImage
from app.domain.generation.schemas.generated_image import GeneratedImageCreate
from app.domain.generation.schemas.generated_image_group import GeneratedImageGroupCreate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobUpdate
from app.domain.generation.services.generation_domain_service import are_all_image_generation_jobs_complete
from app.infrastructure.fcm.fcm_service import FCMService, get_fcm_service
from app.infrastructure.repositories.generation.generation import GeneratedImageRepository, \
    GeneratedImageGroupRepository, GenerationRequestRepository, ImageGenerationJobRepository, \
    get_generation_request_repository, get_image_generation_job_repository, get_generated_image_repository, \
    get_generated_image_group_repository


class ManageGenerationApplicationService:
    def __init__(
            self,
            generation_request_repo: GenerationRequestRepository,
            image_generation_job_repo: ImageGenerationJobRepository,
            generated_image_repo: GeneratedImageRepository,
            generated_image_group_repo: GeneratedImageGroupRepository,
            fcm_service: FCMService
    ):
        self.generation_request_repo = generation_request_repo
        self.image_generation_job_repo = image_generation_job_repo
        self.generated_image_repo = generated_image_repo
        self.generated_image_group_repo = generated_image_group_repo
        self.fcm_service = fcm_service

    def __create_generated_image_group(self, generation_request_id: int) -> GeneratedImageGroup:
        user_id = self.generation_request_repo.get(generation_request_id)
        return self.generated_image_group_repo.create(
            obj_in=GeneratedImageGroupCreate(
                user_id=user_id,
                generation_request_id=generation_request_id
            )
        )

    # TODO: Transaction
    def __create_generated_images(self, image_generation_job_list: List[ImageGenerationJob]) -> List[GeneratedImage]:
        if len(image_generation_job_list) <= 0:
            raise ValueError(f"image_generation_job_list의 길이가 {len(image_generation_job_list)} 입니다.")
        generation_request_id = image_generation_job_list[0].generation_request_id
        generation_request = self.generation_request_repo.get(generation_request_id)
        user_id = generation_request.user_id
        generated_image_group = self.__create_generated_image_group(generation_request_id)

        generated_image_list: List[GeneratedImage] = []

        for image_generation_job in image_generation_job_list:
            generated_image_create = GeneratedImageCreate(
                user_id=user_id,
                s3_key=image_generation_job.s3_key,
                webui_png_info=image_generation_job.webui_png_info,
                generation_request_id=generation_request_id,
                generated_image_group_id=generated_image_group.id,
                image_generation_job_id=image_generation_job.id
            )
            generated_image = self.generated_image_repo.create(obj_in=generated_image_create)
            generated_image_list.append(generated_image)

        return generated_image_list

    def __update_image_generation_job(self, image_generation_job: ImageGenerationJob, webui_png_info: str):
        self.image_generation_job_repo.update(
            obj_id=image_generation_job.id,
            obj_in=ImageGenerationJobUpdate(
                webui_png_info=webui_png_info,
                status=GenerationStatusEnum.COMPLETED
            )
        )

    def on_mq_message(self, channel, method, props, body):
        data_dict = json.loads(body)
        message = MQConsumeMessage(**data_dict)

        # 이거 만일 이 함수 실행 여부에 의존하면, 에러 발생해서 메시지 처리 실패했는데 계속 consume 하는 거로 되려나.
        channel.basic_ack(delivery_tag=method.delivery_tag)

        """
        1. ImageGenerationJob 의 status 등 값을 업데이트함.
        2. 10개가 모두 생성 완료되었는지 체크함 - 도메인 로직
        3. 모두 생성된 경우에 대해서 이미지 생성
        4. 이미지 생성 후 프론트엔드에 FCM 알림 전송
        """

        image_generation_job: ImageGenerationJob = self.image_generation_job_repo.get(message.image_generation_job_id)
        self.__update_image_generation_job(image_generation_job, message.webui_png_info)

        # 2. 모두 생성되었는지 확인
        image_generation_job_list: List[ImageGenerationJob] = (
            self.image_generation_job_repo.get_all_by_generation_request(
                generation_request_id=image_generation_job.generation_request_id
            )
        )
        if not are_all_image_generation_jobs_complete(image_generation_job_list):
            return

        # 3. 이미지 생성
        self.__create_generated_images(image_generation_job_list)

        # 4. 클라이언트에 fcm 보내기


def get_manage_generation_application_service(
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        image_generation_job_repo: ImageGenerationJobRepository = Depends(get_image_generation_job_repository),
        generated_image_repo: GeneratedImageRepository = Depends(get_generated_image_repository),
        generated_image_group_repo: GeneratedImageGroupRepository = Depends(get_generated_image_group_repository),
        fcm_service: FCMService = Depends(get_fcm_service)
) -> ManageGenerationApplicationService:
    return ManageGenerationApplicationService(
        generation_request_repo=generation_request_repo,
        image_generation_job_repo=image_generation_job_repo,
        generated_image_repo=generated_image_repo,
        generated_image_group_repo=generated_image_group_repo,
        fcm_service=fcm_service
    )


