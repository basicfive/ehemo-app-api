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
            print(f"Error creating presigned URL: {e}")
            return None

def get_s3_client() -> S3Client:
    return S3Client(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("REGION_NAME"),
        bucket_name=os.getenv("BUCKET_NAME")
    )
