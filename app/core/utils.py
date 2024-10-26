from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, date, UTC
import uuid
from PIL import Image
import requests
from io import BytesIO
import logging


def remove_duplicates_set(lst: List[int]) -> List[int]:
    return list(set(lst))

def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

def model_list_to_dict(model_list: List[DeclarativeBase]) -> Dict[str, List[Dict[str, Any]]]:
    if not model_list:
        return {}

    model_name = model_list[0].__class__.__name__
    return {
        model_name: [
            {column.name: serialize_datetime(getattr(item, column.name))
             for column in item.__table__.columns.values()}
            for item in model_list
        ]
    }

def generate_unique_datatime_uuid_key(prefix: str) -> str:
    now = datetime.now(UTC)
    unique_id = uuid.uuid4()
    return f"{prefix}{now.strftime('%Y%m%d_%H%M%S')}_{str(unique_id)}"

def concatenate_images_horizontally(image_urls: List[str]) -> Tuple[bytes, str]:
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




def compress_and_resize_image(image_bytes: bytes, scale_factor: float = 0.5, quality: int = 85) -> Tuple[bytes, str]:
    """
    이미지 바이트 데이터를 받아서 해상도를 줄이고 품질을 조정하여 압축된 이미지를 반환합니다.

    Args:
        image_bytes (bytes): 원본 이미지의 바이트 데이터
        scale_factor (float): 축소 비율 (0.5는 50%를 의미)
        quality (int): JPEG 압축 품질 (1-100, 기본값 85)

    Returns:
        Tuple[bytes, str]: (압축된 이미지의 바이트 데이터, 이미지 형식)
    """
    try:
        # 바이트 데이터를 PIL Image 객체로 변환
        img = Image.open(BytesIO(image_bytes))

        # 원본 이미지 형식 저장
        original_format = img.format if img.format else 'JPEG'

        # 새로운 크기 계산
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)

        # LANCZOS 리샘플링을 사용하여 이미지 리사이징
        # Lanczos 알고리즘은 고품질의 안티엘리어싱을 제공합니다
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 압축된 이미지를 저장할 BytesIO 객체 생성
        output_buffer = BytesIO()

        # PNG인 경우 optimize=True로 설정하여 파일 크기 최적화
        if original_format == 'PNG':
            resized_img.save(
                output_buffer,
                format=original_format,
                optimize=True
            )
        # JPEG인 경우 quality 파라미터를 사용하여 압축률 조정
        else:
            # RGBA 이미지를 RGB로 변환 (JPEG는 알파 채널을 지원하지 않음)
            if resized_img.mode == 'RGBA':
                resized_img = resized_img.convert('RGB')

            resized_img.save(
                output_buffer,
                format='JPEG',
                quality=quality,
                optimize=True
            )
            original_format = 'JPEG'

        # 처리된 이미지를 바이트로 변환
        compressed_bytes = output_buffer.getvalue()

        return compressed_bytes, original_format

    except Exception as e:
        logging.error(f"이미지 압축 중 오류 발생: {str(e)}")
        raise