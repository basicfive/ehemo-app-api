from typing import List, Optional
from datetime import datetime, UTC

from app.core.config import image_generation_settings
from app.domain.generation.models.enums.generation_status import GenerationStatusEnum, GenerationResultEnum
from app.domain.generation.models.generation import ImageGenerationJob, GenerationRequest


def _estimate_queue_wait_sec(
        image_count: int,
        processor_count: int,
        buffer_mult: float,
) -> int:
    """
        Args:
        image_count (int): 처리해야하는 이미지 갯수
        processor_count (int): 연결된 이미지 생성 서버 갯수
        buffer_mult (float): 처리 시간 곱 (버퍼값)
    Returns:
        Tuple[bytes, str]: (압축된 이미지의 바이트 데이터, 이미지 형식)
    """
    # ETA_BUFFER_MULTIPLIER * ((이미지 1개 생성 시간) * (현재 mq queue 에 존재하는 요청 수 + 추론 서버 수(현재 처리 갯수))) / (추론 서버 수)
    return int(
        buffer_mult * image_generation_settings.SINGLE_INFERENCE_SEC_EST * (image_count + processor_count) / processor_count
    )

def estimate_normal_priority_message_wait_sec(
        image_count: int,
        processor_count: int,
) -> int:
    return _estimate_queue_wait_sec(image_count, processor_count, buffer_mult=image_generation_settings.WAIT_TIME_BUFFER_MULT)

def estimate_high_priority_message_wait_sec(
        image_count: int,
        processor_count: int,
) -> int:
    # 재시도 시 우선순위 높은 메시지만 고려하므로, queue에 모든 메시지가 높은 우선순위를 갖고 있다는 최악의 경우로 계산
    # 사실 그렇게 따지면 일반 우선순위와 계산 동일하게 하는게 맞긴함.
    return _estimate_queue_wait_sec(image_count, processor_count, buffer_mult=image_generation_settings.RETRY_WAIT_TIME_BUFFER_MULT)

def _calculate_message_ttl_sec(
        multiplier: float
) -> int:
    return int(
        image_generation_settings.SINGLE_INFERENCE_SEC_EST * multiplier
    )

def calculate_normal_message_ttl_sec():
    return _calculate_message_ttl_sec(multiplier=image_generation_settings.MESSAGE_TTL_MULTIPLIER)

def calculate_retry_message_ttl_sec():
    return _calculate_message_ttl_sec(multiplier=image_generation_settings.RETRY_MESSAGE_TTL_MULTIPLIER)

def are_all_image_generation_jobs_complete(image_generation_job_list: List[ImageGenerationJob]):
    for image_generation_job in image_generation_job_list:
        if image_generation_job.status != GenerationStatusEnum.COMPLETED:
            return False
    return True

def calculate_remaining_generation_sec(image_generation_job_list: List[ImageGenerationJob]) -> int:
    print("calculating remaining sec: ")
    # 가장 늦은 expires_at 찾기
    latest_expire = max(job.expires_at for job in image_generation_job_list)

    print(f"latest_expire: {latest_expire}")
    print(f"current time : {datetime.now(UTC)}")

    # 현재 UTC 시간과의 차이 계산
    time_difference = latest_expire - datetime.now(UTC)

    # 음수가 되면(만료시간이 지났으면) 0 반환, 아니면 초 단위로 변환하여 반환
    return max(0, int(time_difference.total_seconds()))

def should_create_image_group(generation_request: GenerationRequest, jobs: List[ImageGenerationJob]) -> bool:
    """
    이미지 그룹 생성 조건 확인
    1. 모든 job 이 완료되었는가.
    2. generation request 가 cancel 되지 않았는가.
    """
    if are_all_image_generation_jobs_complete(jobs):
        return generation_request.generation_result == GenerationResultEnum.PENDING
    return False

def is_generation_in_progress(latest_generation_request: Optional[GenerationRequest]):
    if latest_generation_request is None or \
            latest_generation_request.generation_result != GenerationResultEnum.PENDING:
        return False
    return True