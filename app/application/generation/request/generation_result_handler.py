import json
import logging
from typing import List, Tuple
from datetime import datetime, timedelta, UTC

from app.core.config import rabbit_mq_settings
from app.application.generation.request.dto.upscale_mq import UpscalePublishMessage, UpscaleImageInfo
from app.domain.generation.models.generated_image import GeneratedImage
from app.domain.generation.models.generation import GenerationJob, GenerationRequest
from app.domain.user.models.user import User
from app.core.constants import FCMConstants
from app.infrastructure.database.transaction import transactional
from app.application.generation.request.dto.generation_mq import GenerationConsumeMessage
from app.domain.generation.services.generation_request_service import GenerationRequestService
from app.infrastructure.mq.rabbit_mq_service import RabbitMQService
from app.application.transactional_service import TransactionalService
from app.infrastructure.database.unit_of_work import UnitOfWork
from app.infrastructure.fcm.fcm_service import FCMService
from app.infrastructure.repositories.user.user import UserRepository
from app.infrastructure.repositories.generation.generation import GenerationRequestRepository
from app.infrastructure.s3.s3_client import S3Client

logger = logging.getLogger(__name__)

class GenerationResultHandler(TransactionalService):
    def __init__(
            self,
            user_repo: UserRepository,
            generation_request_service: GenerationRequestService,
            generation_request_repo: GenerationRequestRepository,
            rabbit_mq_service: RabbitMQService,
            fcm_service: FCMService,
            s3_client: S3Client,
            unit_of_work: UnitOfWork,
    ):
        super().__init__(unit_of_work)
        self.user_repo = user_repo
        self.generation_request_service = generation_request_service
        self.generation_request_repo = generation_request_repo
        self.rabbit_mq_service = rabbit_mq_service
        self.fcm_service = fcm_service
        self.s3_client = s3_client

    async def handle_generation_result(self, body: bytes) -> None:
        data_dict = json.loads(body)
        message = GenerationConsumeMessage(**data_dict)
        logger.info(f"[MQ] Consumed Job ID: {message.generation_job_id}. DETAILS: {message.model_dump_json()}")

        if message.is_success:
            generation_job, generated_images = self.mark_after_generation_success(message.generation_job_id)
            generation_request = self.generation_request_repo.get_with_resolution(generation_job.generation_request_id)

            if generation_request.image_resolution.is_high_resolution:
                for generated_image in generated_images:
                    await self._resize_and_reupload_image(generated_image.s3_key)

            time_delta: timedelta = (generation_job.expires_at - datetime.now(UTC))
            await self._request_generated_image_upscale(
                generation_job_id=generation_job.id,
                generated_image_list=generated_images,
                time_to_live_sec=int(time_delta.total_seconds()),
                prompt=generation_job.prompt,
                width=generation_job.width,
                height=generation_job.height,
            )
        else:
            generation_request, generation_job, generated_images = self.mark_as_failed(message.generation_job_id)
            user: User = self.user_repo.get(generation_request.user_id)
            self._notify_user_failure(generation_request.id, user)

    @transactional
    def mark_after_generation_success(self, generation_job_id: int) -> Tuple[GenerationJob, List[GeneratedImage]]:
        return self.generation_request_service.mark_after_generation_success(generation_job_id)
    
    @transactional
    def mark_as_failed(self, generation_job_id: int) -> Tuple[GenerationRequest, GenerationJob, List[GeneratedImage]]:
        return self.generation_request_service.mark_as_failed(generation_job_id)

    async def _request_generated_image_upscale(
            self,
            generation_job_id: int,
            generated_image_list: List[GeneratedImage],
            time_to_live_sec: int,
            prompt: str,
            width: int,
            height: int,
    ):
        image_info_list: List[UpscaleImageInfo] = []
        for generated_image in generated_image_list:
            image_info_list.append(
                UpscaleImageInfo(
                    generated_image_id=generated_image.id,
                    s3_key=generated_image.s3_key,
                    upscale_s3_key=generated_image.upscaled_s3_key,
                )
            )
        message = UpscalePublishMessage(
            generation_job_id=generation_job_id,
            image_info_list=image_info_list,
            time_to_live_sec=time_to_live_sec,
            prompt=prompt,
            width=width,
            height=height,
        )
        await self.rabbit_mq_service.publish(
            message=message.model_dump_json(),
            queue_name=rabbit_mq_settings.RABBITMQ_UPSCALE_PUBLISH,
            expiration_sec=message.time_to_live_sec,
        )

    def _notify_user_failure(
            self,
            generation_request_id: int,
            user: User,
    ):
        self.fcm_service.send_to_token(
            token=user.fcm_token,
            title=FCMConstants.FAILURE_TITLE,
            body=FCMConstants.FAILURE_BODY,
            data={"generation_request_id": str(generation_request_id)},
        )

    async def _resize_and_reupload_image(self, s3_key: str) -> None:
        """
        S3에서 이미지를 다운로드하여 크기를 반으로 줄인 후 동일한 키에 재업로드합니다.
        
        Args:
            s3_key (str): 이미지의 S3 키
        """
        from app.core.utils import compress_and_resize_image
        import requests
        from io import BytesIO
        
        # S3에서 이미지 다운로드를 위한 presigned URL 생성
        download_url = self.s3_client.create_get_presigned_url(s3_key)
        if not download_url:
            logger.error(f"Failed to create presigned URL for downloading: {s3_key}")
            return
        
        try:
            # 이미지 다운로드
            response = requests.get(download_url)
            response.raise_for_status()
            image_bytes = response.content
            
            # 이미지 리사이징 (가로, 세로 각각 반으로 줄임 = 면적 1/4)
            compressed_bytes, image_format = compress_and_resize_image(
                image_bytes=image_bytes,
                scale_factor=0.5,  # 가로, 세로 각각 50%로 축소
                quality=100
            )
            
            # 동일한 S3 키에 리사이징된 이미지 업로드
            upload_success = self.s3_client.upload_to_s3(
                key=s3_key,
                image_data=compressed_bytes,
                image_format=image_format
            )
            
            if upload_success:
                logger.info(f"Successfully resized and reuploaded image: {s3_key}")
            else:
                logger.error(f"Failed to upload resized image: {s3_key}")
                
        except Exception as e:
            logger.error(f"Error during image resize process for {s3_key}: {str(e)}")

from app.core.db.base import get_db
from app.infrastructure.database.unit_of_work import get_unit_of_work
from app.infrastructure.repositories.generation.generation import get_generation_request_repository, get_generation_job_repository
from app.infrastructure.repositories.generation.generated_image import get_generated_image_repository
from app.infrastructure.repositories.user.user import get_user_repository
from app.infrastructure.fcm.fcm_service import get_fcm_service
from app.infrastructure.mq.rabbit_mq_service import get_rabbit_mq_service_singleton
from app.domain.generation.services.generation_request_service import get_generation_request_service
from app.infrastructure.s3.s3_client import get_s3_client

async def handle_generation_result(body: bytes) -> None:
    db = next(get_db())
    try:
        generation_request_repo = get_generation_request_repository(db)
        generation_request_service = get_generation_request_service(
            generation_request_repository=generation_request_repo,
            generation_job_repository=get_generation_job_repository(db),
            generated_image_repository=get_generated_image_repository(db),
        )
        message_handler = GenerationResultHandler(
            user_repo=get_user_repository(db),
            generation_request_service=generation_request_service,
            generation_request_repo=generation_request_repo,
            rabbit_mq_service=await get_rabbit_mq_service_singleton(),
            fcm_service=get_fcm_service(),
            s3_client=get_s3_client(),
            unit_of_work=get_unit_of_work(db),
        )
        await message_handler.handle_generation_result(body)
    finally:
        db.close()
