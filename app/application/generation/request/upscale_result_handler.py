import json
from typing import List, Tuple

from app.domain.token.models.token import TokenWallet
from app.domain.token.models.token import TokenSourceType
from app.domain.user.models.user import User
from app.infrastructure.repositories.user.user import UserRepository
from app.core.constants import FCMConstants, GenerationMessageData
from app.infrastructure.fcm.fcm_service import FCMService
from app.application.generation.request.dto.upscale_mq import NormalUpscaleConsumeMessage
from app.domain.generation.models.generation import GenerationJob, GenerationRequest
from app.domain.generation.models.generated_image import GeneratedImage
from app.infrastructure.database.transaction import transactional
from app.domain.generation.services.generation_request_service import GenerationRequestService
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.domain.token.services.token_domain_sevice import TokenService
from app.application.transactional_service import TransactionalService

class UpscaleResultHandler(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            generation_request_service: GenerationRequestService,
            token_service: TokenService,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.generation_request_service = generation_request_service
        self.token_service = token_service
        self.fcm_service = fcm_service
    
    def handle_upscale_result(self, body: bytes) -> None:
        dict_data = json.loads(body)
        message = NormalUpscaleConsumeMessage(**dict_data)

        if message.is_success:
            generation_request, generation_job, generated_images = self.mark_as_success(message.generation_job_id)
        else:
            generation_request, generation_job, generated_images = self.mark_as_failed(message.generation_job_id)

        user: User = self.user_repo.get(generation_request.user_id)
        self._notify_user(user, message.is_success, generation_request.id)

    @transactional
    def mark_as_success(self, generation_job_id: int) -> Tuple[GenerationRequest, GenerationJob, List[GeneratedImage]]:
        return self.generation_request_service.mark_as_success(generation_job_id)

    @transactional
    def mark_as_failed(self, generation_job_id: int) -> Tuple[GenerationRequest, GenerationJob, List[GeneratedImage]]:
        generation_request, generation_job, generated_images = self.generation_request_service.mark_as_failed(generation_job_id)

        user: User = self.user_repo.get_with_token_wallets(generation_request.user_id)
        token_wallet: TokenWallet = user.current_token_wallet

        self.token_service.refund_token(
            token_wallet=token_wallet,
            amount=generation_request.consumed_tokens,
            source_type=TokenSourceType.IMAGE_GENERATION,
        )

        return generation_request, generation_job, generated_images
    
    def _notify_user(
            self,
            user: User,
            is_success: bool,
            generation_request_id: int,
    ):
        if is_success:
            self.fcm_service.send_to_token(
                token=user.fcm_token,
                title=FCMConstants.GENERATION_SUCCESS_TITLE,
                body=FCMConstants.GENERATION_SUCCESS_BODY,
                data=GenerationMessageData(
                    generation_request_id=generation_request_id,
                ).model_dump_str(),
            )
        else:
            self.fcm_service.send_to_token(
                token=user.fcm_token,
                title=FCMConstants.GENERATION_FAILURE_TITLE,
                body=FCMConstants.GENERATION_FAILURE_BODY,
                data=GenerationMessageData(
                    generation_request_id=generation_request_id,
                ).model_dump_str(),
            )


from app.core.db.base import get_db
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.repositories.generation.generation import get_generation_job_repository, get_generation_request_repository
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.repositories.user.user import get_user_repository
from app.domain.generation.services.generation_request_service import get_generation_request_service
from app.domain.token.services.token_domain_sevice import get_token_service
from app.infrastructure.fcm.fcm_service import get_fcm_service
from app.infrastructure.repositories.token.token import get_token_wallet_repository, get_token_transaction_repository

def handle_upscale_result(body: bytes) -> None:
    db = next(get_db())
    try:
        generation_job_repository = get_generation_job_repository(db)
        generation_request_repository = get_generation_request_repository(db)
        generated_image_repository = get_generated_image_repository(db)
        generation_request_service: GenerationRequestService = get_generation_request_service(
            generation_job_repository=generation_job_repository,
            generation_request_repository=generation_request_repository,
            generated_image_repository=generated_image_repository,
        )
        token_wallet_repository = get_token_wallet_repository(db)
        token_transaction_repository = get_token_transaction_repository(db)
        token_service: TokenService = get_token_service(
            token_wallet_repo=token_wallet_repository,
            token_transaction_repo=token_transaction_repository,
        )
        user_repo: UserRepository = get_user_repository(db)
        fcm_service: FCMService = get_fcm_service()
        unit_of_work: UnitOfWork = get_unit_of_work(db)

        service = UpscaleResultHandler(
            user_repo=user_repo,
            generation_request_service=generation_request_service,
            token_service=token_service,
            fcm_service=fcm_service,
            unit_of_work=unit_of_work,
        )
        service.handle_upscale_result(body)
    finally:
        db.close()
