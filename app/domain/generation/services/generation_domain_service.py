from typing import List

from app.core.constants import SINGLE_IMAGE_INFERENCE_SEC
from app.core.enums.generation_status import GenerationStatusEnum
from app.domain.generation.models.generation import ImageGenerationJob


def calculate_generation_sec(image_count: int, processor_count: int) -> int:
    if processor_count == 0:
        # TODO: 에러처리
        return -1
    # ((이미지 1개 생성 시간) * (현재 mq queue 에 존재하는 요청 수 + 추론 서버 수(현재처리 중))) / (추론 서버 수)
    return int(SINGLE_IMAGE_INFERENCE_SEC * (image_count + processor_count) / processor_count)

def are_all_image_generation_jobs_complete(image_generation_job_list: List[ImageGenerationJob]):
    for image_generation_job in image_generation_job_list:
        if image_generation_job.status != GenerationStatusEnum.COMPLETED:
            return False
    return True

