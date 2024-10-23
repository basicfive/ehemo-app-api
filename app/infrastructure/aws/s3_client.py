import logging
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

class S3Client:
    def __init__(
            self,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            region_name: str,
            bucket_name: str
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

    def create_presigned_url(
            self,
            s3_key: str,
            expiration: int = 600,
            http_method: str = 'GET'
    ) -> Optional[str]:
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
            return response
        except ClientError as e:
            logging.error(f"Error creating presigned URL: {e}")
            return None

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
    return S3Client(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("REGION_NAME"),
        bucket_name=os.getenv("BUCKET_NAME")
    )
