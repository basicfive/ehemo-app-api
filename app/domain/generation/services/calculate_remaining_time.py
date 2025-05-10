from typing import Tuple, List

from app.infrastructure.repositories.generation.generation import GenerationJobRepository
from app.domain.generation.models.generation import GenerationJob
from app.core.config import image_generation_settings

class CalculateRemainingTimeService:
    def __init__(
            self,
            generation_job_repo: GenerationJobRepository
    ):
        self.generation_job_repo = generation_job_repo
    
    def _get_generation_wait_time(self, pending_jobs_with_resolution: List[GenerationJob], generation_consumer_count: int) -> int:
        # 고화질 이미지, 기본 이미지 갯수 구하기
        high_resolution_pending_image_count = 0
        default_resolution_pending_image_count = 0

        for pending_job in pending_jobs_with_resolution:
            if pending_job.generation_request.image_resolution.is_high_resolution:
                high_resolution_pending_image_count += pending_job.image_count
            else:
                default_resolution_pending_image_count += pending_job.image_count

        # 이미지 생성 예상 시간 = ((고화질 대기 * 고화질 생성 예상 시간) + (기본 대기 * 기본 생성 예상 시간)) / 생성 서버
        generation_time = (
            (high_resolution_pending_image_count * image_generation_settings.SINGLE_INFERENCE_HIGH_RES_SEC_EST)
            + (default_resolution_pending_image_count * image_generation_settings.SINGLE_INFERENCE_SEC_EST)
        ) / generation_consumer_count
        
        return generation_time
    
    def _get_upscale_wait_time(self, pending_upscale_jobs: List[GenerationJob], upscale_consumer_count: int) -> int:
        # 업스케일 이미지 갯수
        pending_upscale_images_count = 0
        for pending_upscale_job in pending_upscale_jobs:
            pending_upscale_images_count += pending_upscale_job.image_count

        # 예상 업스케일 시간 = ((생성 대기 이미지 + 업스케일 대기 이미지) * 이미지 1개당 업스케일 예상 시간) / 업스케일 서버
        upscale_time = (
            pending_upscale_images_count * image_generation_settings.SINGLE_INFERENCE_UPSCALE_SEC_EST
        ) / upscale_consumer_count

        return upscale_time

    def get_generation_upscale_wait_time(self, generation_consumer_count: int, upscale_consumer_count: int) -> Tuple[int, int]:
        pending_jobs_with_resolution = self.generation_job_repo.get_pending_jobs_with_resolution()
        pending_upscale_jobs = self.generation_job_repo.get_pending_upscale_jobs()

        pending_upscale_jobs += pending_jobs_with_resolution

        generation_time = self._get_generation_wait_time(pending_jobs_with_resolution, generation_consumer_count)
        upscale_time = self._get_upscale_wait_time(pending_upscale_jobs, upscale_consumer_count)

        return generation_time, upscale_time
    
    def _get_single_generation_duration(self, is_high_resolution: bool, image_count: int) -> int:
        if is_high_resolution:
            time = image_generation_settings.SINGLE_INFERENCE_HIGH_RES_SEC_EST
        else:
            time = image_generation_settings.SINGLE_INFERENCE_SEC_EST
        return time * image_count
    
    def _get_single_upscale_duration(self, image_count: int) -> int:
        return image_generation_settings.SINGLE_INFERENCE_UPSCALE_SEC_EST * image_count

    def get_generation_job_expire_time(
            self,
            is_high_resolution: bool,
            generation_consumer_count: int,
            upscale_consumer_count: int,
            image_count: int = image_generation_settings.GENERATED_IMAGE_CNT_PER_REQUEST,
        ) -> int:
        generation_duration = self._get_single_generation_duration(is_high_resolution, image_count)
        upscale_duration = self._get_single_upscale_duration(image_count)
        """
        MAX(
            (생성 작업 대기 시간 + 현재 이미지 작업 시간),
            (업스케일 대기 시간 + 현재 이미지 작업 시간 + 업스케일 시간)
        ) * 여유 버퍼 (1.2)
        """
        generation_wait_time, upscale_wait_time = self.get_generation_upscale_wait_time(
            generation_consumer_count=generation_consumer_count,
            upscale_consumer_count=upscale_consumer_count,
        )
        duration = max(
            generation_wait_time + generation_duration,
            upscale_wait_time + generation_duration + upscale_duration
        ) 
        return int(duration * image_generation_settings.IMAGE_GENERATION_JOB_EXPIRE_TIME_MULTIPLIER)


from fastapi import Depends
from app.infrastructure.repositories.generation.generation import get_generation_job_repository

def get_calculate_remaining_time_service(
    generation_job_repo: GenerationJobRepository = Depends(get_generation_job_repository),
) -> CalculateRemainingTimeService:
    return CalculateRemainingTimeService(generation_job_repo)
