from pydantic import BaseModel

class UploadedImagesForTrainingCreate(BaseModel):
    user_id: int
    s3_key: str
    training_request_id: int

class UploadedImagesForTrainingUpdate(BaseModel):
    pass

class UploadedImagesForTrainingInDB(BaseModel):
    id: int
    user_id: int
    s3_key: str
    training_request_id: int

    class Config:
        from_attributes = True