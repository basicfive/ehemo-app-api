from pydantic import BaseModel

class HairStyleOptionRequest(BaseModel):
    gender_id: int

class HairStyleLengthOptionRequest(BaseModel):
    hair_style_id: int

class HairDesignColorOptionRequest(BaseModel):
    hair_style_id: int
    length_id: int

