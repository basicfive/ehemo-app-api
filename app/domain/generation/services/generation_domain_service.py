from typing import List

from app.core.config import image_generation_setting
from app.core.enums.generation_status import GenerationStatusEnum
from app.domain.generation.models.generation import ImageGenerationJob


def calculate_generation_eta_sec(image_count: int, processor_count: int) -> int:
    if processor_count == 0:
        return -1
    # ETA_BUFFER_MULTIPLIER * ((이미지 1개 생성 시간) * (현재 mq queue 에 존재하는 요청 수 + 추론 서버 수(현재 처리 갯수))) / (추론 서버 수)
    return int(
        image_generation_setting.ETA_BUFFER_MULTIPLIER * (
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

