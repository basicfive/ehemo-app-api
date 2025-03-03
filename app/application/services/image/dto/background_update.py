from pydantic import BaseModel


class LastModifiedImageUploadDto(BaseModel):
    generated_image_id: int
    upload_presigned_url: str
    s3_key: str