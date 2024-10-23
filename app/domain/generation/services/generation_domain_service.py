from typing import List
from PIL import Image
import requests
from io import BytesIO

from app.core.constants import SINGLE_IMAGE_INFERENCE_SEC
from app.core.enums.generation_status import GenerationStatusEnum
from app.domain.generation.models.generation import ImageGenerationJob


def calculate_generation_sec(image_count: int, processor_count: int) -> int:
    return int(SINGLE_IMAGE_INFERENCE_SEC * image_count / processor_count)

def are_all_image_generation_jobs_complete(image_generation_job_list: List[ImageGenerationJob]):
    for image_generation_job in image_generation_job_list:
        if image_generation_job.status != GenerationStatusEnum.COMPLETED:
            return False
    return True


def concatenate_images_horizontally(image_urls):
    """
    이미지 URL 리스트를 받아서 이미지들을 가로로 연결하여 바이트 스트림으로 반환

    Args:
        image_urls (List[str]): 이미지 URL들이 담긴 리스트

    Returns:
        bytes: 가로로 연결된 이미지의 바이트 데이터
        str: 이미지 형식 (예: 'JPEG', 'PNG')
    """

    if not len(image_urls):
        return None

    # 이미지들을 담을 리스트 초기화
    images = []

    # URL에서 이미지 다운로드
    for url in image_urls:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        # 원본 이미지 형식 저장
        image_format = img.format if img.format else 'JPEG'
        images.append(img)

    # 첫 번째 이미지의 크기 가져오기
    img_width, img_height = images[0].size

    # 결과 이미지의 크기 계산
    total_width = img_width * len(images)

    # 새로운 이미지 생성
    result_image = Image.new('RGB', (total_width, img_height))

    # 이미지들을 가로로 붙이기
    for idx, img in enumerate(images):
        result_image.paste(img, (idx * img_width, 0))

    # 이미지를 바이트로 변환
    img_byte_arr = BytesIO()
    result_image.save(img_byte_arr, format=image_format)
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr, image_format
