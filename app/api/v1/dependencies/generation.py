from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.generation import GenerationRequestRepository
from app.services.generation import GenerationRequestService

def get_generation_request_repository(db: Session = Depends(get_db)) -> GenerationRequestRepository:
    return GenerationRequestRepository(db=db)

def get_generation_request_service(
        repo: GenerationRequestRepository = Depends(get_generation_request_repository)
) -> GenerationRequestService:
    return GenerationRequestService(repo=repo)