
import logging
from typing import List, Tuple

from app.domain.token.models.token import TokenWallet
from app.domain.token.enums.token import TokenSourceType
from app.domain.generation.models.generated_image import GeneratedImage
from app.domain.generation.models.generation import GenerationJob, GenerationRequest
from app.domain.user.models.user import User
from app.core.constants import FCMConstants, GenerationMessageData
from app.infrastructure.database.transaction import transactional
from app.domain.generation.services.generation_request_service import GenerationRequestService
from app.application.transactional_service import TransactionalService
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository
from app.infrastructure.s3.s3_client import S3Client
from app.infrastructure.runpod.dto import WebhookResponse
from app.domain.token.services.token_domain_sevice import TokenService

logger = logging.getLogger(__name__)

class GenerationResultHandler(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            generation_request_service: GenerationRequestService,
            generation_request_repo: GenerationRequestRepository,
            token_service: TokenService,
            fcm_service: FCMService,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.generation_request_service = generation_request_service
        self.generation_request_repo = generation_request_repo
        self.token_service = token_service
        self.fcm_service = fcm_service
        self.s3_client = s3_client

    def handle_generation_result(self, result: WebhookResponse) -> None:

        is_success = result.is_success

        if is_success:
            generation_request, generation_job, generated_images = self.mark_as_success(result.job_id)
        else:
            generation_request, generation_job, generated_images = self.mark_as_failed(result.job_id)

        user: User = self.user_repo.get(generation_request.user_id)
        self._notify_user(user, result.is_success, generation_request.id)

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




from fastapi import Depends
from app.infrastructure.repositories.user.user import get_user_repository
from app.domain.generation.services.generation_request_service import get_generation_request_service
from app.infrastructure.repositories.generation.generation import get_generation_request_repository
from app.infrastructure.fcm.fcm_service import get_fcm_service
from app.infrastructure.s3.s3_client import get_s3_client
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.domain.token.services.token_domain_sevice import get_token_service

def get_generation_result_handler(
        user_repo: UserRepository = Depends(get_user_repository),
        generation_request_service: GenerationRequestService = Depends(get_generation_request_service),
        generation_request_repo: GenerationRequestRepository = Depends(get_generation_request_repository),
        token_service: TokenService = Depends(get_token_service),
        fcm_service: FCMService = Depends(get_fcm_service),
        s3_client: S3Client = Depends(get_s3_client),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),
) -> GenerationResultHandler:
    return GenerationResultHandler(
        user_repo=user_repo,
        generation_request_service=generation_request_service,
        generation_request_repo=generation_request_repo,
        token_service=token_service,
        fcm_service=fcm_service,
        s3_client=s3_client,
        unit_of_work=unit_of_work,
    )

