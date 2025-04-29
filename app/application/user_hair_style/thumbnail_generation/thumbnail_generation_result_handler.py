import json

from app.application.user_hair_style.thumbnail_generation.dto.thumbnail_mq import ThumbnailGenerationConsumeMessage
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.application.transactional_service import TransactionalService
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.database.transaction import transactional
from app.core.constants import FCMConstants
from app.domain.training.models.user_hair_style import UserHairStyleLora
from app.infrastructure.repositories.training.training import TrainingRequestRepository
from app.infrastructure.repositories.training.user_hair_style import UserHairStyleLoraRepository, UserHairStyleRepository
from app.infrastructure.fcm.fcm_service import FCMService
from app.domain.training.models.training import TrainingRequest
from app.domain.user.models.user import User
from app.domain.training.models.user_hair_style import UserHairStyle
from app.domain.training.schemas.user_hair_style.user_hair_style import UserHairStyleCreate
from app.domain.common.enums.ai_status import TrainingRequestStatus
from app.domain.training.schemas.training.training_request import TrainingRequestUpdate

class ThumbnailGenerationResultHandler(TransactionalService):
    def __init__(
            self,
            user_hair_style_repository: UserHairStyleRepository,
            user_hair_style_lora_repository: UserHairStyleLoraRepository,
            training_request_repository: TrainingRequestRepository,
            rabbitmq_service: RabbitMQService,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_hair_style_repository = user_hair_style_repository
        self.training_request_repository = training_request_repository
        self.user_hair_style_lora_repository = user_hair_style_lora_repository
        self.rabbitmq_service = rabbitmq_service
        self.fcm_service = fcm_service

    @transactional
    def _handle_thumbnail_generation_result(
        self,
        message: ThumbnailGenerationConsumeMessage,
        training_request: TrainingRequest,
        user: User,
    ):
        # 헤어스타일 등록
        user_hair_style_lora: UserHairStyleLora = self.user_hair_style_lora_repository.get_by_request(message.training_request_id)

        user_hair_style: UserHairStyle = self.user_hair_style_repository.create_with_flush(
            obj_in=UserHairStyleCreate(
                user_id=user.id,
                thumbnail_s3_key=message.thumbnail_s3_key,
                title=training_request.title,
                description=training_request.description,
                user_hair_style_lora_id=user_hair_style_lora.id,
            )
        )
        # request 상태 변경
        self.training_request_repository.update_with_flush(
            obj_id=training_request.id,
            obj_in=TrainingRequestUpdate(
                status=TrainingRequestStatus.COMPLETED,
            )
        )

    def handle_thumbnail_generation_result(self, body: bytes):
        data_dict = json.loads(body)
        message = ThumbnailGenerationConsumeMessage(**data_dict)
        
        training_request: TrainingRequest = self.training_request_repository.get_with_user(message.training_request_id)
        user: User = training_request.user

        self._handle_thumbnail_generation_result(message, training_request, user)

        # 유저에게 등록 완료를 알리는 push 전송
        self.fcm_service.send_to_token(
            token=user.fcm_token,
            title=FCMConstants.USER_HAIRSTYLE_REGISTER_COMPLETED_TITLE,
            body=FCMConstants.USER_HAIRSTYLE_REGISTER_COMPLETED_BODY,
        )


from app.core.db.base import get_db

async def handle_thumbnail_generation_result(body: bytes) -> None:
    db = next(get_db())
    try:
        usecase = ThumbnailGenerationResultHandler(
            user_hair_style_repository=UserHairStyleRepository(db),
            user_hair_style_lora_repository=UserHairStyleLoraRepository(db),
            training_request_repository=TrainingRequestRepository(db),
            rabbitmq_service=RabbitMQService(),
            fcm_service=FCMService(),
            unit_of_work=UnitOfWork(db),
        )
        await usecase.handle_thumbnail_generation_result(body)
    finally:
        db.close()
