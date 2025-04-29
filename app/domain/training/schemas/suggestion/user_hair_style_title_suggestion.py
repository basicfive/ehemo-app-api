from pydantic import BaseModel

class UserHairStyleTitleSuggestionCreate(BaseModel):
    title: str

class UserHairStyleTitleSuggestionUpdate(BaseModel):
    pass

class UserHairStyleTitleSuggestionInDB(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True
