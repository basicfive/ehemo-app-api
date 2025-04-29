from pydantic import BaseModel

class UserHairStyleDescriptionSuggestionCreate(BaseModel):
    description: str

class UserHairStyleDescriptionSuggestionUpdate(BaseModel):
    pass

class UserHairStyleDescriptionSuggestionInDB(BaseModel):
    id: int
    description: str
    
    class Config:
        from_attributes = True