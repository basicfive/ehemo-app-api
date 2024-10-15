from pydantic import BaseModel
import os

from dotenv import load_dotenv

load_dotenv()

class Setting(BaseModel):
    PROJECT_NAME: str = "ehemo-app-api"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL:str = os.getenv("DATABASE_URL")

settings = Setting()