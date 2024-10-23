from typing import List, Dict, Any
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, date, UTC
import uuid
import random
from PIL import Image
import requests
from io import BytesIO


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

def generate_unique_datatime_uuid_key() -> str:
    now = datetime.now(UTC)
    unique_id = uuid.uuid4()
    return f"{now.strftime('%Y%m%d_%H%M%S')}_{str(unique_id)}"

def concatenate_images_horizontally(image_urls: List[str]):
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
