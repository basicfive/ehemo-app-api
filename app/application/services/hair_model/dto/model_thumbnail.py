from pydantic import BaseModel

class ModelThumbnailData(BaseModel):
    gender_id: int
    presigned_image_url: str