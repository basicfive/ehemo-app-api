from fastapi import APIRouter, Depends

from app.services.user import UserService
from app.schemas.user import UserCreate
from app.api.v1.dependencies.hair import get_user_service

router = APIRouter()

@router.post("/create")
def create_user(
    user_create: UserCreate,
    service: UserService = Depends(get_user_service)
):
    pass
