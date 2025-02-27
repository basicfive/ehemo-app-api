import logging
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

from app.core.config import aws_s3_settings


class S3Client:
    def __init__(
            self,
            aws_access_key_id: str = aws_s3_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key: str = aws_s3_settings.AWS_SECRET_ACCESS_KEY,
            region_name: str = aws_s3_settings.REGION_NAME,
            bucket_name: str = aws_s3_settings.BUCKET_NAME
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.bucket_name = bucket_name

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
            config=Config(signature_version='s3v4')  # SigV4 서명 사용
        )

    def _create_presigned_url(
            self,
            action: str,
            params: Dict[str, Any],
            expiration: int = aws_s3_settings.PRESIGNED_URL_EXPIRATION_SEC,
            http_method: str = 'GET'
    ) -> Optional[str]:
        """
        S3 작업을 위한 presigned URL을 생성하는 내부 헬퍼 함수

        Args:
            action (str): S3 작업 타입 ('get_object', 'put_object' 등)
            params (Dict[str, Any]): S3 작업에 필요한 파라미터
            expiration (int): URL 만료 시간 (초)
            http_method (str): HTTP 메서드

        Returns:
            Optional[str]: 성공시 presigned URL, 실패시 None
        """
        try:
            response = self.s3_client.generate_presigned_url(
                action,
                Params=params,
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
            return response
        except ClientError as e:
            logging.error(f"Error creating presigned URL for {action}: {e}")
            return None

    def create_get_presigned_url(
            self,
            s3_key: str,
            expiration: int = aws_s3_settings.PRESIGNED_URL_EXPIRATION_SEC
    ) -> Optional[str]:
        """
        S3에서 객체를 다운로드하기 위한 GET presigned URL 생성

        Args:
            s3_key (str): 접근할 S3 객체 키
            expiration (int): URL 만료 시간 (초)

        Returns:
            Optional[str]: 성공시 presigned URL, 실패시 None
        """
        params = {
            'Bucket': self.bucket_name,
            'Key': s3_key
        }
        return self._create_presigned_url(
            action='get_object',
            params=params,
            expiration=expiration,
            http_method='GET'
        )

    def create_put_presigned_url(
            self,
            s3_key: str,
            content_type: str = 'image/jpeg',
            expiration: int = aws_s3_settings.PRESIGNED_URL_EXPIRATION_SEC
    ) -> Optional[str]:
        """
        S3에 객체를 업로드하기 위한 PUT presigned URL 생성

        Args:
            s3_key (str): 업로드할 S3 객체 키
            content_type (str): 업로드할 파일의 컨텐츠 타입
            expiration (int): URL 만료 시간 (초)

        Returns:
            Optional[str]: 성공시 presigned URL, 실패시 None
        """
        params = {
            'Bucket': self.bucket_name,
            'Key': s3_key,
            'ContentType': content_type
        }
        return self._create_presigned_url(
            action='put_object',
            params=params,
            expiration=expiration,
            http_method='PUT'
        )

    def upload_to_s3(self, key, image_data, image_format='JPEG'):
        """
        이미지 데이터를 S3에 업로드

        Args:
            key (str): S3에 저장될 객체 이름 (경로 포함)
            image_data (bytes): 업로드할 이미지 바이트 데이터
            image_format (str): 이미지 형식 (기본값: 'JPEG')

        Returns:
            bool: 업로드 성공 여부
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType=f'image/{image_format.lower()}'
            )
            return True

        except ClientError as e:
            logging.error(e)
            return False

def get_s3_client() -> S3Client:
    return S3Client()
