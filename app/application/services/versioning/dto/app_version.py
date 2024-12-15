from pydantic import BaseModel

class CheckVersionResponse(BaseModel):
    requires_update: bool
    suggests_update: bool
    store_url: str
