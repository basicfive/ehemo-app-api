import logging
from datetime import datetime, timedelta, UTC
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from app import fcm_consts, token_settings
from app.application.services.generation.dto.mq import MQPublishMessage
from app.application.services.generation.dto.retry import FailedJobResult
from app.application.services.transactional_service import TransactionalService
from app.core.db.base import get_db
from app.domain.generation.models.enums.generation_status import GenerationStatusEnum, GenerationResultEnum
from app.core.enums.message_priority import MessagePriority
from app.core.errors.exceptions import NoInferenceConsumerException
from app.domain.generation.models.generation import ImageGenerationJob, GenerationRequest
from app.domain.generation.schemas.generation_request import GenerationRequestUpdate
from app.domain.generation.schemas.image_generation_job import ImageGenerationJobUpdate, ImageGenerationJobInDB
from app.domain.generation.services.generation_domain_service import estimate_high_priority_message_wait_sec, calculate_retry_message_ttl_sec
from app.domain.token.models.enums.token import TokenSourceType
from app.domain.token.models.token import TokenWallet
from app.domain.token.services.token_domain_sevice import TokenDomainService, get_token_domain_service
from app.domain.user.models.user import User
from app.infrastructure.database.transaction import transactional
from app.infrastructure.database.unit_of_work import UnitOfWork, get_unit_of_work
from app.infrastructure.fcm.dto.fcm_message import FCMGenerationResultData
from app.infrastructure.fcm.fcm_service import FCMService, get_fcm_service
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.infrastructure.repositories.generation.generation import ImageGenerationJobRepository, \
    GenerationRequestRepository, get_image_generation_job_repository, get_generation_request_repository
from app.core.config import image_generation_settings
from app.infrastructure.repositories.token.token import get_token_wallet_repository, get_token_transaction_repository
from app.infrastructure.repositories.user.user import UserRepository, get_user_repository

logger = logging.getLogger()

class ImageGenerationRetryService(TransactionalService):
    def __init__(
            self,
            image_generation_job_repo: ImageGenerationJobRepository,
            generation_request_repo: GenerationRequestRepository,
            user_repo: UserRepository,
            token_domain_service: TokenDomainService,
            rabbit_mq_service: RabbitMQService,
            fcm_service: FCMService,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.image_generation_job_repo = image_generation_job_repo
        self.generation_request_repo = generation_request_repo
        self.user_repo = user_repo
        self.token_domain_service = token_domain_service
        self.rabbit_mq_service = rabbit_mq_service
        self.fcm_service = fcm_service

    async def retry_expired_jobs(self):
        expired_jobs = self._get_expired_jobs()
        logger.info(f"Found {len(expired_jobs)} expired jobs to process...")
        if not expired_jobs:
            return

        message_count, consumer_count = await self._validate_queue_state()
        current_message_expire_at = estimate_high_priority_message_wait_sec(
            image_count=message_count,
            processor_count=consumer_count
        )

        for expired_job in expired_jobs:
            if expired_job.retry_count >= image_generation_settings.MAX_RETRIES:
                # [FAILED 처리]
                self._handle_failed_job(expired_job)
            else:
                current_message_expire_at = await self._retry_job(expired_job, current_message_expire_at)


    def _get_expired_jobs(self) -> List[ImageGenerationJob]:
        return self.image_generation_job_repo.get_all_expired_but_to_process_jobs()

    async def _validate_queue_state(self) -> Tuple[int, int]:
        message_count, consumer_count = await self.rabbit_mq_service.get_queue_info()
        if consumer_count < 1:
            raise NoInferenceConsumerException()
        return message_count, consumer_count


    @transactional
    async def _retry_job(self, expired_job: ImageGenerationJob, current_message_expire_at: int) -> int:

            print(f"Currently updating expire time with retry - current time : {datetime.now(UTC)}")
            new_expire_at = current_message_expire_at + calculate_retry_message_ttl_sec()

            # 재요청 - mq 높은 우선순위
            db_retry_job = self.image_generation_job_repo.update_with_flush(
                obj_id=expired_job.id,
                obj_in=ImageGenerationJobUpdate(
                    retry_count=expired_job.retry_count + 1,
                    expires_at=datetime.now(UTC) + timedelta(seconds=new_expire_at)
                )
            )
            retry_job = ImageGenerationJobInDB.model_validate(db_retry_job)
            message = MQPublishMessage(
                **retry_job.model_dump(),
                image_generation_job_id=retry_job.id,
            )

            await self.rabbit_mq_service.publish(
                message=message,
                expiration_sec=new_expire_at,
                priority=MessagePriority.URGENT
            )

            return new_expire_at

    def _handle_failed_job(self, expired_job: ImageGenerationJob):
        failed_result: Optional[FailedJobResult] = self._mark_as_job_failed(expired_job)

        # generation request 중 최초라면
        if failed_result:
            try:
                self._send_failure_notification(failed_result.user.fcm_token)
            except Exception:
                logger.error(
                    f"Failed to send FCM notification for job {failed_result.image_generation_job_id} "
                    f"(request: {failed_result.generation_request_id})"
                )
                raise

    @transactional
    def _mark_as_job_failed(self, expired_job: ImageGenerationJob) -> Optional[FailedJobResult]:
        self.image_generation_job_repo.update(
            obj_id=expired_job.id,
            obj_in=ImageGenerationJobUpdate(status=GenerationStatusEnum.FAILED)
        )
        logger.info(f"Job ID: {expired_job.id} has exhausted all retry attempts. Marked as failed.")

        # 아직 fcm 에러를 보내지 않았다면, fcm 전송 후 generation request 업데이트
        generation_request: GenerationRequest = self.generation_request_repo.get(expired_job.generation_request_id)
        if generation_request.generation_result == GenerationResultEnum.PENDING:

            user_with_wallet: User = self.user_repo.get_with_token_wallet(generation_request.user_id)

            # 구독 토큰 반환
            token_wallet: TokenWallet = user_with_wallet.token_wallet
            self.token_domain_service.refund_token(
                token_wallet=token_wallet,
                amount=token_settings.TOKENS_PER_GENERATION,
                source_type=TokenSourceType.IMAGE_GENERATION,
            )

            self.generation_request_repo.update(
                obj_id=generation_request.id,
                obj_in=GenerationRequestUpdate(generation_result=GenerationResultEnum.FAILED)
            )
            logger.info(f"Generation Request: {generation_request.id} is marked as failed.")

            return FailedJobResult(
                user=user_with_wallet,
                image_generation_job_id=expired_job.id,
                generation_request_id=generation_request.id,
            )
        return None

    def _send_failure_notification(self, fcm_token: str):
        fcm_data = FCMGenerationResultData(generation_status=GenerationResultEnum.FAILED)
        self.fcm_service.send_to_token(
            token=fcm_token,
            title=fcm_consts.FAILURE_TITLE,
            body=fcm_consts.FAILURE_BODY,
            data=fcm_data.to_fcm_data(),
        )

async def retry_expired_jobs(
        rabbit_mq_service: RabbitMQService,
):
    db: Session = next(get_db())
    try:
        service = ImageGenerationRetryService(
            image_generation_job_repo = get_image_generation_job_repository(db),
            generation_request_repo = get_generation_request_repository(db),
            user_repo=get_user_repository(db),
            token_domain_service=get_token_domain_service(
                token_wallet_repo=get_token_wallet_repository(db),
                token_transaction_repo=get_token_transaction_repository(db),
            ),
            rabbit_mq_service=rabbit_mq_service,
            fcm_service=get_fcm_service(),
            unit_of_work=get_unit_of_work(db),
        )
        await service.retry_expired_jobs()
    finally:
        db.close()
