from typing import List, Dict, Any
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, date
import random

# import os
# import boto3
# from botocore.exceptions import ClientError
#
# s3_client = boto3.client('s3')
# BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
#
# def create_presigned_url(s3_key, expiration: int = 600, http_method: str ='GET'):
#     try:
#         response = s3_client.generated_presigned_url(
#             'get_object',
#             Params={'Bucket' : BUCKET_NAME, 'Key' : s3_key},
#             ExpiresIn=expiration,
#             HttpMethod=http_method
#         )
#     except ClientError as e:
#         print(f"{e}")
#         return None
#
#     return response

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

def create_prompt(
        gender_prompt: str,
        length_prompt: str,
        color_prompt: str,
        posture_and_clothing_prompt: str,
        background_prompt: str,
        lora_model_prompt: str
) -> str:
    age: int = random.randint(20, 29)
    """
    A 25-year-old Korean woman with blonde long ohwx hair,
    close-up shot, looking over shoulder, in a cozy cowl-neck sweater, hair falling in soft layers with subtle highlights,
    against white wall <lora:fx_layered_1-000200:1>
    """
    return f"A {age}-year-old Korean {gender_prompt} with {color_prompt} {length_prompt} ohwx hair, {posture_and_clothing_prompt}, against {background_prompt} {lora_model_prompt}"
