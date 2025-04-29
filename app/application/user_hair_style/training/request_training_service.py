from uuid import uuid4
from sqlalchemy.exc import NoResultFound

from app.domain.training.models.training import TrainingJob
from app.application.user_hair_style.training.dto.training_mq import TrainingPublishMessage
from app.core.config import training_settings, rabbit_mq_settings
from app.domain.user.models.user import User
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.core.errors.http_exceptions import ValueException
from app.application.user_hair_style.training.dto.request_training import UserHairStyleRegisterRequest, UserHairStyleRegisterResponse
from app.application.transactional_service import TransactionalService
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.domain.training.services.training_request_service import TrainingRequestService
from app.domain.training.services.user_hair_lora_naming import create_user_hair_lora_name, create_user_hair_lora_s3_key

class RequestTrainingService(TransactionalService):
    def __init__(
            self,
            user_repository: UserRepository,
            training_request_service: TrainingRequestService,
            rabbit_mq_service: RabbitMQService,
            unit_of_work: UnitOfWork,
        ):
        super().__init__(unit_of_work)
        self.user_repository = user_repository
        self.training_request_service = training_request_service
        self.rabbit_mq_service = rabbit_mq_service


    @transactional
    async def request_training(self, request: UserHairStyleRegisterRequest) -> UserHairStyleRegisterResponse:
        # 1. 업로드 된 이미지 갯수 validation (서버 쪽에서 한 번 더)
        if len(request.uploaded_image_s3_keys) < training_settings.MINIMUM_IMAGE_CNT_FOR_TRAINING:
            raise ValueException(f"이미지는 최소 {training_settings.MINIMUM_IMAGE_CNT_FOR_TRAINING}개 이상이어야해요")
        if len(request.uploaded_image_s3_keys) > training_settings.MAXIMUM_IMAGE_CNT_FOR_TRAINING:
            raise ValueException(f"이미지 최대 갯수 {training_settings.MAXIMUM_IMAGE_CNT_FOR_TRAINING}를 초과했어요")

        # 2. 사용자 존재 여부 확인
        try:
            user: User = self.user_repository.get(request.user_id)
        except Exception:
            raise ValueException("사용자를 찾을 수 없습니다.")

        # 3. 현재 진행 중인 training 있는지 확인
        if self.training_request_service.is_user_training_job_pending(user.id):
            raise ValueException("현재 등록 중인 헤어스타일이 있어요. 등록이 완료된 후 새로운 스타일을 등록해주세요")

        images_for_training, training_request, training_job = self.training_request_service.create_training_request_and_job(
            gender=request.gender,
            user=user,
            title=request.title,
            description=request.description,
            uploaded_images_s3_keys=request.uploaded_image_s3_keys,
        )

        user_hair_lora_name: str = create_user_hair_lora_name()
        user_hair_lora_s3_key: str = create_user_hair_lora_s3_key(user_hair_lora_name)

        await self.rabbit_mq_service.publish(
            message=TrainingPublishMessage(
                gender=training_job.gender,
                training_job_id=training_job.id,
                user_hair_lora_s3_key=user_hair_lora_s3_key,
                user_hair_lora_name=user_hair_lora_name,
                uploaded_image_s3_keys=[image_for_training.s3_key for image_for_training in images_for_training],
                total_steps=training_job.total_steps,
                epoch=training_job.epoch,
            ).model_dump_json(),
            queue_name=rabbit_mq_settings.RABBITMQ_TRAINING_PUBLISH,
        )

        estimated_time_sec: int = self.training_request_service.calculate_training_request_eta_sec()
        return UserHairStyleRegisterResponse(
            estimated_time_sec=estimated_time_sec,
        )


from fastapi import Depends
from app.infrastructure.repositories.user.user import get_user_repository
from app.domain.training.services.training_request_service import get_training_request_service
from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service
from app.infrastructure.database.unit_of_work import get_unit_of_work

def get_request_training_service(
        user_repository: UserRepository = Depends(get_user_repository),
        training_request_service: TrainingRequestService = Depends(get_training_request_service),
        rabbit_mq_service: RabbitMQService = Depends(get_rabbit_mq_service),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> RequestTrainingService:
    return RequestTrainingService(
        user_repository=user_repository,
        training_request_service=training_request_service,
        rabbit_mq_service=rabbit_mq_service,
        unit_of_work=unit_of_work,
    )