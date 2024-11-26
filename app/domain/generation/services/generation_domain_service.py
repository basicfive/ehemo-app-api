from typing import List
from datetime import datetime, UTC

from app.core.config import image_generation_setting
from app.core.enums.generation_status import GenerationStatusEnum
from app.domain.generation.models.generation import ImageGenerationJob


def calculate_generation_eta_sec(
        image_count: int,
        processor_count: int,
        buffer_mult: float = image_generation_setting.ETA_BUFFER_MULTIPLIER
) -> int:
    """
        Args:
        image_count (int): 처리해야하는 이미지 갯수
        processor_count (int): 연결된 이미지 생성 서버 갯수
        buffer_mult (float): 처리 시간 곱 (버퍼값)
    Returns:
        Tuple[bytes, str]: (압축된 이미지의 바이트 데이터, 이미지 형식)
    """
    if processor_count == 0:
        return -1
    # ETA_BUFFER_MULTIPLIER * ((이미지 1개 생성 시간) * (현재 mq queue 에 존재하는 요청 수 + 추론 서버 수(현재 처리 갯수))) / (추론 서버 수)
    return int(
        buffer_mult * (
            image_generation_setting.SINGLE_IMAGE_INFERENCE_SEC * (image_count + processor_count) / processor_count
        )
    )

def calculate_single_generation_sec(processor_count: int) -> int:
    if processor_count == 0:
        return -1
    return int(image_generation_setting.SINGLE_IMAGE_INFERENCE_SEC / processor_count)


def are_all_image_generation_jobs_complete(image_generation_job_list: List[ImageGenerationJob]):
    for image_generation_job in image_generation_job_list:
        if image_generation_job.status != GenerationStatusEnum.COMPLETED:
            return False
    return True

def calculate_remaining_generation_sec(image_generation_job_list: List[ImageGenerationJob]) -> int:

    # 가장 늦은 expires_at 찾기
    latest_expire = max(job.expires_at for job in image_generation_job_list)

    # 현재 UTC 시간과의 차이 계산
    time_difference = latest_expire - datetime.now(UTC)

    # 음수가 되면(만료시간이 지났으면) 0 반환, 아니면 초 단위로 변환하여 반환
    return max(0, int(time_difference.total_seconds()))

