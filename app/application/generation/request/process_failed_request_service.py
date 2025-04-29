import logging
from datetime import datetime, timedelta, UTC
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from app.core.config import base_settings
from app.infrastructure.alert.discord_webhook import send_error_notification
from app.domain.generation.services.generation_request_service import GenerationRequestService
from app.domain.token.models.token import TokenWallet
from app.domain.token.enums.token import TokenSourceType
from app.domain.generation.schemas.generation.generation_request import GenerationRequestUpdate
from app.domain.generation.schemas.generation.generation_job import GenerationJobUpdate
from app import FCMConstants, token_settings
from app.domain.generation.models.generation import GenerationRequest
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository
from app.infrastructure.repositories.user.user import UserRepository
from app.domain.token.services.token_domain_sevice import TokenService
from app.domain.user.models.user import User
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.application.transactional_service import TransactionalService
from app.infrastructure.fcm.fcm_service import FCMService
from app.domain.generation.models.generation import GenerationJob
from app.infrastructure.repositories.generation.generation import GenerationJobRepository

logger = logging.getLogger()

class ProcessFailedRequestService(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            generation_job_repo: GenerationJobRepository,
            generation_request_service: GenerationRequestService,
            token_domain_service: TokenService,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.generation_job_repo = generation_job_repo
        self.generation_request_service = generation_request_service
        self.token_domain_service = token_domain_service
        self.fcm_service = fcm_service

    def process_failed_requests(self):
        expired_jobs = self.generation_job_repo.get_all_expired_but_to_process_jobs()
        logger.info(f"Found {len(expired_jobs)} expired jobs to mark as failed...")

        for expired_job in expired_jobs:
            self._mark_as_failed_and_notify(expired_job)


    def _mark_as_failed_and_notify(self, expired_job: GenerationJob):
        fcm_token = self._mark_as_job_failed(expired_job)

        try:
            self.fcm_service.send_to_token(
                token=fcm_token,
                title=FCMConstants.FAILURE_TITLE,
                body=FCMConstants.FAILURE_BODY,
            )
        except Exception as e:
            logger.error(
                f"Failed to send FCM notification for job {expired_job.id} "
                f"(request: {expired_job.generation_request_id})"
            )
            send_error_notification(webhook_url=base_settings.ALERT_DISCORD_WEBHOOK, error=e)


    @transactional
    def _mark_as_job_failed(self, expired_job: GenerationJob) -> str:
        logger.info(f"Job ID: {expired_job.id} has exhausted all retry attempts. Marked as failed.")

        generation_request, _, _ = self.generation_request_service.mark_as_failed(expired_job.id)

        user_with_wallet: User = self.user_repo.get_with_token_wallets(generation_request.user_id)

        # 구독 토큰 반환
        token_wallet: TokenWallet = user_with_wallet.current_token_wallet
        self.token_domain_service.refund_token(
            token_wallet=token_wallet,
            amount=generation_request.consumed_tokens,
            source_type=TokenSourceType.IMAGE_GENERATION,
        )
        return user_with_wallet.fcm_token


from app.core.db.base import get_db
from app.infrastructure.repositories.user.user import get_user_repository
from app.domain.generation.services.generation_request_service import get_generation_request_service
from app.domain.token.services.token_domain_sevice import get_token_service
from app.infrastructure.repositories.token.token import get_token_wallet_repository
from app.infrastructure.repositories.token.token import get_token_transaction_repository
from app.infrastructure.fcm.fcm_service import get_fcm_service
from app.infrastructure.repositories.generation.generation import get_generation_job_repository
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.repositories.generation.generation import get_generation_request_repository
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.repositories.generation.hair_style import get_hair_style_repository
from app.infrastructure.repositories.training.user_hair_style import get_user_hair_style_repository
from app.infrastructure.repositories.generation.image_resolution import get_image_resolution_repository
from app.infrastructure.repositories.generation.generation import get_request_prompt_component_question_answer_repository

def process_failed_requests():
    db: Session = next(get_db())
    try:
        token_wallet_repo=get_token_wallet_repository(db)
        token_transaction_repo=get_token_transaction_repository(db)
        generation_request_repository=get_generation_request_repository(db)
        generation_job_repository=get_generation_job_repository(db)
        generated_image_repository=get_generated_image_repository(db)

        hair_style_repository=get_hair_style_repository(db)
        user_hair_style_repository=get_user_hair_style_repository(db)
        image_resolution_repository=get_image_resolution_repository(db)
        request_prompt_component_question_answer_repository=get_request_prompt_component_question_answer_repository(db)

        service = ProcessFailedRequestService(
            user_repo=get_user_repository(db),
            generation_job_repo=generation_job_repository,
            generation_request_service=get_generation_request_service(
                generation_request_repository=generation_request_repository,
                generation_job_repository=generation_job_repository,
                generated_image_repository=generated_image_repository,
                hair_style_repository=hair_style_repository,
                user_hair_style_repository=user_hair_style_repository,
                image_resolution_repository=image_resolution_repository,
                request_prompt_component_question_answer_repository=request_prompt_component_question_answer_repository,
            ),
            token_domain_service=get_token_service(
                token_wallet_repo=token_wallet_repo,
                token_transaction_repo=token_transaction_repo,
            ),
            fcm_service=get_fcm_service(),
            unit_of_work=get_unit_of_work(db),
        )
        service.process_failed_requests()
    finally:
        db.close()
