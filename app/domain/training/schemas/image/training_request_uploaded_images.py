from pydantic import BaseModel

class TrainingRequestUploadedImagesCreate(BaseModel):
    training_request_id: int
    uploaded_images_for_training_id: int

class TrainingRequestUploadedImagesUpdate(BaseModel):
    pass

class TrainingRequestUploadedImagesInDB(BaseModel):
    id: int
    training_request_id: int
    uploaded_images_for_training_id: int

    class Config:
        from_attributes = True