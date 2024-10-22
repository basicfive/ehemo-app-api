from pydantic import BaseModel


class GenderOption(BaseModel):
    id: int
    title: str
    description: str
    presigned_image_url: str
    order: int

class HairStyleOption(BaseModel):
    id: int
    title: str
    description: str
    presigned_image_url: str
    order: int

class HairStyleLengthOption(BaseModel):
    id: int
    title: str
    description: str
    presigned_image_url: str
    order: int
    length_id: int

class HairDesignColorOption(BaseModel):
    id: int
    title: str
    description: str
    presigned_image_url: str
    order: int
    color_id: int

class BackgroundOption(BaseModel):
    id: int
    title: str
    description: str
    presigned_image_url: str
    order: int

class ImageResolutionOption(BaseModel):
    id: int
    title: str
    description: str
    presigned_image_url: str
    order: int